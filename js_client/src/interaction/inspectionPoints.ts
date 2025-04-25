import * as monaco from 'monaco-editor';
import { editor } from "../monacoExperiment";

/**
 * Updates the decorations in the editor.
 * @param lineCount The total number of lines in the editor.
 * @param clickedLines A set of line numbers that are clicked.
 * @param decorationsCollection The decorations collection to update.
 */

const model = editor.getModel();
if (!model) {
    console.error("No model is attached to the editor.");
}

let lineCount = model.getLineCount();
const decorationsCollection = editor.createDecorationsCollection([]);
const clickedLines = new Set<number>();

// Initialize decorations
updateDecorations(lineCount, clickedLines, decorationsCollection);

// Update decorations on content change
model.onDidChangeContent(() => {
    const newLineCount = model.getLineCount();
    if (newLineCount !== lineCount) {
        lineCount = newLineCount;
        updateDecorations(lineCount, clickedLines, decorationsCollection);
    }
});

// Event listen for decoration or line number click
editor.onMouseDown((event) => {
    if (
        event.target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN ||
        event.target.type === monaco.editor.MouseTargetType.GUTTER_LINE_NUMBERS
    ) {
        const lineNumber = event.target.position?.lineNumber;
        if (lineNumber) {
            if (clickedLines.has(lineNumber)) {
                clickedLines.delete(lineNumber);
            } else {
                clickedLines.add(lineNumber);
            }
            updateDecorations(lineCount, clickedLines, decorationsCollection);
        }
    }
});

function updateDecorations(
lineCount: number,
clickedLines: Set<number>,
decorationsCollection: monaco.editor.IEditorDecorationsCollection
) {
const decorations = [];
for (let i = 1; i <= lineCount; i++) {
    decorations.push({
        range: new monaco.Range(i, 1, i, 1),
        options: {
            isWholeLine: false,
            glyphMarginClassName: clickedLines.has(i)
                ? 'red-circle-decoration'
                : 'red-circle-decoration opacity'
        },
    });
}

decorationsCollection.set(decorations);
}