import {ResponseMessageType} from "../responseMessages/responseMessageDefinitions";
import {
    CommandMessage,
    InspectionPointFormat, InspectionPointMessage,
    UserMessageType
} from "./userMessageDefinitions";


export function createCommandMessage(id: number, command: string): CommandMessage {
    return {
        type: UserMessageType.Command,
        data: {
            id: id,
            command: command,
        }
    };
}

export function createInspectionPointFormat(id: number, lineNumber: number, command: string): InspectionPointFormat {
    return {
        id: id,
        lineNumber: lineNumber,
        command: command,
    };
}

export function createDebugMessage(scriptLines: string[], inspectionPoints: InspectionPointFormat[]): InspectionPointMessage {
    return {
        type: UserMessageType.Debug,
        data: {
            script: scriptLines,
            inspectionPoints: inspectionPoints,
        }
    };
}