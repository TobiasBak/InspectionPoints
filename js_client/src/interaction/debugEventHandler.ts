import { editor } from "../monacoExperiment";
import { decorationIds, model } from "./inspectionPoints";
import { createDebugMessage, createInspectionPointFormat } from "../userMessages/userMessageFactory";
import { InspectionPointFormat } from "../userMessages/userMessageDefinitions";
import { BeginDebugEvent } from "./EventList";

export function createDebugEvent(): BeginDebugEvent {
    const inspectionPointsMap = new Map<number, InspectionPointFormat>();
    let idCounter = 1;

    decorationIds.forEach((lineNumber, decorationId) => {
        const range = model.getDecorationRange(decorationId);
        if (range) {
            const currentLineNumber = range.startLineNumber;
            const lineContent = model.getLineContent(currentLineNumber);
            inspectionPointsMap.set(
                currentLineNumber,
                createInspectionPointFormat(idCounter++, currentLineNumber, lineContent)
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