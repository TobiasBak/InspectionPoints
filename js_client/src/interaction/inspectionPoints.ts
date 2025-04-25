import * as monaco from 'monaco-editor';
import { editor } from "../monacoExperiment";

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

//WIP
function getDecoratedLines(): { type: string; data: { script: string[]; inspectionPoints: { id: number; lineNumber: number; command: string }[] } } {
    const decoratedLines: { id: number; lineNumber: number; command: string }[] = [];
    let idCounter = 1;

    decorationIds.forEach((lineNumber, id) => {
        const range = model.getDecorationRange(id);
        if (range) {
            const currentLineNumber = range.startLineNumber;
            const lineContent = model.getLineContent(currentLineNumber);
            decoratedLines.push({
                id: idCounter++,
                lineNumber: currentLineNumber,
                command: lineContent.trim(),
            });
        }
    });

    const scriptAndInspectionPoints = {
        type: "Debug",
        data: {
            script: model.getLinesContent(),
            inspectionPoints: decoratedLines,
        },
    };

    return scriptAndInspectionPoints;
}


// MOVE THIS AND MAKE IT EMIT A CUSTOM EVENT
// This is just for testing purposes
// to see the decorated lines in the console
const button = document.getElementById("debugEditorButton");
if (button) {
    button.addEventListener("click", () => {
        console.log(getDecoratedLines());
    });
}
