import { editor } from "../monacoExperiment";
import { decorationIds, model } from "./inspectionPoints";
import { inspectionVariables } from "./inspectionPopupManager";
import { selectedGlobalVariables } from "../cobotVariableSelection";
import {createInspectionPointFormat, createDebugMessageData} from '../userMessages/userMessageFactory';
import {InspectionPointFormat, InspectionVariable} from '../userMessages/userMessageDefinitions';
import { BeginDebugEvent } from "./EventList";

const idMap = new Map<number, number>();

export function getLineNumberFromInspectionPointId(id: number): number{
    return idMap.get(id) ?? -1;
}

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

            idMap.set(idCounter, currentLineNumber);

            inspectionPointsMap.set(
                currentLineNumber,
                createInspectionPointFormat(idCounter++, currentLineNumber, lineContent, additionalVariables)
            );
        }
    });

    const inspectionPoints = Array.from(inspectionPointsMap.values()).sort(
        (a, b) => a.lineNumber - b.lineNumber
    );

    const globalVariables: InspectionVariable[] = selectedGlobalVariables;
    const messageData = createDebugMessageData(model.getLinesContent(), inspectionPoints, globalVariables);
    return new BeginDebugEvent(messageData);
}

document.getElementById("debugEditorButton")?.addEventListener("click", () => {
    const debugEvent = createDebugEvent();
    document.dispatchEvent(debugEvent);
    console.log("Debug event dispatched:", debugEvent);

    localStorage.setItem('urscript', editor.getValue());
});