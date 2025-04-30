import { editor } from "../monacoExperiment";
import { decorationIds } from "./inspectionPoints";
import { createDebugMessage } from "../userMessages/userMessageFactory";
import { BeginDebugEvent } from "./EventList";

export function createDebugEvent(): BeginDebugEvent {
    const inspectionPointsMap = new Map<number, any>();
    let idCounter = 1;

    decorationIds.forEach((lineNumber, decorationId) => {
        const range = editor.getModel()?.getDecorationRange(decorationId);
        if (range) {
            const currentLineNumber = range.startLineNumber;
            const lineContent = editor.getModel()?.getLineContent(currentLineNumber) || "";
            inspectionPointsMap.set(
                currentLineNumber,
                { id: idCounter++, lineNumber: currentLineNumber, content: lineContent }
            );
        }
    });

    const inspectionPoints = Array.from(inspectionPointsMap.values()).sort(
        (a, b) => a.lineNumber - b.lineNumber
    );

    const debugMessage = createDebugMessage(editor.getModel()?.getLinesContent() || [], inspectionPoints).data;
    return new BeginDebugEvent(debugMessage);
}

const debugButton = document.getElementById("debugEditorButton");
if (debugButton) {
    debugButton.addEventListener("click", () => {
        const debugEvent = createDebugEvent();
        document.dispatchEvent(debugEvent);
        console.log("Debug event dispatched:", debugEvent);
    });
}