import * as monaco from 'monaco-editor';
import { editor } from "../monacoExperiment";
import { createInspectionPointFormat, createDebugMessage } from '../userMessages/userMessageFactory';
import { InspectionPointMessageData, InspectionPointFormat } from '../userMessages/userMessageDefinitions';
import { BeginDebugEvent } from './EventList';

const model = editor.getModel();
if (!model) {
    throw new Error("No model is attached to the editor.");
}

const decorationIds = new Map<string, number>();

editor.onMouseDown((event) => {
    if (
        event.target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN ||
        event.target.type === monaco.editor.MouseTargetType.GUTTER_LINE_NUMBERS
    ) {
        const lineNumber = event.target.position?.lineNumber;
        if (!lineNumber) return;

        // Check if decoration is on this line
        let existingId: string | undefined;
        decorationIds.forEach((line, id) => {
            if (line === lineNumber) {
                existingId = id;
            }
        });

        if (existingId) {
            // Remove decoration
            model.deltaDecorations([existingId], []);
            decorationIds.delete(existingId);
        } else {
            // Add decoration
            const [newId] = model.deltaDecorations([], [
                {
                    range: new monaco.Range(lineNumber, 1, lineNumber, 1),
                    options: {
                        isWholeLine: true,
                        glyphMarginClassName: 'red-circle-decoration',
                        stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
                    },
                },
            ]);

            decorationIds.set(newId, lineNumber);
        }
    }
});

// Function to collect decorated lines and create a debug message
function collectDecoratedLines(): InspectionPointMessageData {
    const inspectionPoints: InspectionPointFormat[] = [];
    let idCounter = 1;

    decorationIds.forEach((lineNumber, decorationId) => {
        const range = model.getDecorationRange(decorationId);
        if (range) {
            const currentLineNumber = range.startLineNumber;
            const lineContent = model.getLineContent(currentLineNumber);
            inspectionPoints.push(
                createInspectionPointFormat(idCounter++, currentLineNumber, lineContent)
            );
        }
    });

    const debugMessage = createDebugMessage(model.getLinesContent(), inspectionPoints).data;
    return debugMessage;
}

const debugButton = document.getElementById("debugEditorButton");
//Ensure the button exists
if (debugButton) {
    debugButton.addEventListener("click", () => {
        const debugData = collectDecoratedLines();

        const debugEvent = new BeginDebugEvent(debugData);
        document.dispatchEvent(debugEvent);

        console.log("Debug event dispatched:", debugEvent);
    });
}
