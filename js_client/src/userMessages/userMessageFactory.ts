import {
    CommandMessage,
    InspectionPointFormat, InspectionPointMessage, InspectionVariable, InspectionPointMessageData,
    UserMessageType, StopCommandMessage
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

export function createInspectionPointFormat(id: number, lineNumber: number, command: string, additionalVariables: InspectionVariable[]): InspectionPointFormat {
    return {
        id: id,
        lineNumber: lineNumber,
        command: command,
        additionalVariablesToRead: additionalVariables,
    };
}

export function createDebugMessageData(scriptLines: string[], inspectionPoints: InspectionPointFormat[], globalVariables: InspectionVariable[]): InspectionPointMessageData {
    return {
        script: scriptLines,
        inspectionPoints: inspectionPoints,
        globalVariables: globalVariables,
    };
}

export function createDebugMessage(data: InspectionPointMessageData): InspectionPointMessage {
    return {
        type: UserMessageType.Debug,
        data: data
    };
}

export function createStopCommandMessage(id: number, command: string): StopCommandMessage {
    return {
        type: UserMessageType.StopCommand,
        data: {
            id: id,
            message: command,
        }
    };
}