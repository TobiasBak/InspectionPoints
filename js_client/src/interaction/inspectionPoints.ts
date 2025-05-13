import * as monaco from 'monaco-editor';
import {editor} from "../monacoExperiment";
import {openPopup, inspectionVariables} from "./inspectionPopupManager";

export const model = editor.getModel();
if (!model) {
    throw new Error("No model is attached to the editor.");
}

export const decorationIds = new Map<string, number>();

editor.onMouseDown((event) => {
    if (
        !(event.target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN ||
        event.target.type === monaco.editor.MouseTargetType.GUTTER_LINE_NUMBERS)
    ){
        return;
    }

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
        if (event.event.rightButton) {
            event.event.preventDefault();
            event.event.stopPropagation();
            openPopup(existingDecorationId, event.event.posx, event.event.posy);
        } else {
            // Remove decoration
            model.deltaDecorations([existingDecorationId], []);
            decorationIds.delete(existingDecorationId);
        }
    } else {
        // Add decoration
        const [newId] = model.deltaDecorations([], [
            {
                range: new monaco.Range(lineNumber, 1, lineNumber, 1),
                options: {
                    isWholeLine: true,
                    glyphMarginClassName: 'inspection-point-decoration',
                    stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
                },
            },
        ]);

        decorationIds.set(newId, lineNumber);
    }
});

editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, function() {
    localStorage.setItem('urscript', editor.getValue());
});

function updateDecorationStyle(decorationId: string) {
    const hasTrackedVariables = inspectionVariables.has(decorationId) && inspectionVariables.get(decorationId)!.length > 0;

    const range = model.getDecorationRange(decorationId);
    if (range) {
        model.deltaDecorations([decorationId], [
            {
                range,
                options: {
                    isWholeLine: true,
                    glyphMarginClassName: hasTrackedVariables
                        ? 'tracked-variable-decoration'
                        : 'inspection-point-decoration',
                    stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
                },
            },
        ]);
    }
}

// Listen for the custom "refreshDecoration" event to update the decoration style
// when the tracked variables are changed
// This event is dispatched in the inspectionPopupManager when a variable is added or removed
document.addEventListener("refreshDecoration", (event: Event) => {
    const customEvent = event as CustomEvent<{ decorationId: string }>;
    const { decorationId } = customEvent.detail;
    updateDecorationStyle(decorationId);
});