import * as monaco from 'monaco-editor';
import {editor} from "../monacoExperiment";
import {createInspectionPointFormat, createDebugMessageData} from '../userMessages/userMessageFactory';
import {InspectionPointFormat, InspectionVariable} from '../userMessages/userMessageDefinitions';
import {BeginDebugEvent} from './EventList';

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
        let existingDecorationId: string | undefined;
        decorationIds.forEach((_, decorationId) => {
            const range = model.getDecorationRange(decorationId);
            if (range && range.startLineNumber === lineNumber) {
                existingDecorationId = decorationId;
            }
        });

        if (existingDecorationId) {
            // Remove decoration
            model.deltaDecorations([existingDecorationId], []);
            decorationIds.delete(existingDecorationId);
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

// Function to collect decorated lines and create a BeginDebugEvent
function createDebugEvent(): BeginDebugEvent {
    const inspectionPointsMap = new Map<number, InspectionPointFormat>();
    let idCounter = 1;

    decorationIds.forEach((lineNumber, decorationId) => {
        const range = model.getDecorationRange(decorationId);
        if (range) {
            const currentLineNumber = range.startLineNumber;
            const lineContent = model.getLineContent(currentLineNumber);


            const additionalVariables: InspectionVariable[] = [];

            inspectionPointsMap.set(
                currentLineNumber,
                createInspectionPointFormat(idCounter++, currentLineNumber, lineContent, additionalVariables)
            );
        }
    });

    const inspectionPoints = Array.from(inspectionPointsMap.values()).sort(
        (a, b) => a.lineNumber - b.lineNumber
    );

    const globalVariables: InspectionVariable[] = [{
        name: "joints",
        readCommand: "get_actual_joint_positions()"
    }]
    const messageData = createDebugMessageData(model.getLinesContent(), inspectionPoints, globalVariables);
    return new BeginDebugEvent(messageData);
}

document.getElementById("debugEditorButton")?.addEventListener("click", () => {
    const debugEvent = createDebugEvent();
    document.dispatchEvent(debugEvent);
    console.log("Debug event dispatched:", debugEvent);
});