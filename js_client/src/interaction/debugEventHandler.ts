import { editor } from "../monacoExperiment";
import { decorationIds, model } from "./inspectionPoints";
import { inspectionVariables } from "./inspectionPopupManager";
import {createInspectionPointFormat, createDebugMessageData} from '../userMessages/userMessageFactory';
import {InspectionPointFormat, InspectionVariable} from '../userMessages/userMessageDefinitions';
import { BeginDebugEvent } from "./EventList";

function createDebugEvent(): BeginDebugEvent {
    const inspectionPointsMap = new Map<number, InspectionPointFormat>();
    let idCounter = 1;

    decorationIds.forEach((lineNumber, decorationId) => {
        const range = model.getDecorationRange(decorationId);
        if (range) {
            const currentLineNumber = range.startLineNumber;
            const lineContent = model.getLineContent(currentLineNumber);

            const trackedVariables = inspectionVariables.get(decorationId) || [];
            const additionalVariables: InspectionVariable[] = trackedVariables.map((variableName) => ({
                name: variableName,
                readCommand: variableName,
            }));

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
    },{
        name: "pose",
        readCommand: "get_actual_tcp_pose()"
    }];
    const messageData = createDebugMessageData(model.getLinesContent(), inspectionPoints, globalVariables);
    return new BeginDebugEvent(messageData);
}

document.getElementById("debugEditorButton")?.addEventListener("click", () => {
    const debugEvent = createDebugEvent();
    document.dispatchEvent(debugEvent);
    console.log("Debug event dispatched:", debugEvent);

    localStorage.setItem('urscript', editor.getValue());
});