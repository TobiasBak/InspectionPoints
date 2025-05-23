// This is supposed to be a definitions file, but typescript is not good with enums in definition files.
// This is not intended to house business logic, but to define the message types that the server and client will use.

export enum UserMessageType {
    Command = 'Command',
    Debug = 'Debug',
    StopCommand = 'StopCommand',
}

export type UserMessage = CommandMessage | InspectionPointMessage | StopCommandMessage;

export type CommandMessageData = {
    id: number,
    command: string,
}

export type CommandMessage = {
    type: UserMessageType.Command,
    data: CommandMessageData
}

export type InspectionVariable = {
    name: string,
    readCommand: string,
}

export type InspectionPointFormat = {
    id: number,
    lineNumber: number,
    command: string,
    additionalVariablesToRead: InspectionVariable[]
}

export type InspectionPointMessageData = {
    script: string[],
    inspectionPoints: InspectionPointFormat[],
    globalVariables: InspectionVariable[]
}

export type InspectionPointMessage = {
    type: UserMessageType.Debug,
    data: InspectionPointMessageData
}

export type StopCommandMessageData = {
    id: number,
    message: string,
}

export type StopCommandMessage = {
    type: UserMessageType.StopCommand,
    data: StopCommandMessageData
}
