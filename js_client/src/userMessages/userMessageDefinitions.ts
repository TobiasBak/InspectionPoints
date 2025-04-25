// This is supposed to be a definitions file, but typescript is not good with enums in definition files.
// This is not intended to house business logic, but to define the message types that the server and client will use.

export enum UserMessageType {
    Command = 'Command',
    Debug = 'Debug'
}

export type UserMessage = CommandMessage | InspectionPointMessage

export type CommandMessageData = {
    id: number,
    command: string,
}

export type CommandMessage = {
    type: UserMessageType.Command,
    data: CommandMessageData
}

export type InspectionPointFormat = {
    id: number,
    lineNumber: number,
    command: string,
}

export type InspectionPointMessageData = {
    script: string[],
    inspectionPoints: InspectionPointFormat[],
}

export type InspectionPointMessage = {
    type: UserMessageType.Debug,
    data: InspectionPointMessageData
}
