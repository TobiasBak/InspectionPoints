// This is supposed to be a definitions file, but typescript is not good with enums in definition files.
// This is not intended to house business logic, but to define the message types that the server and client will use.

export enum ResponseMessageType {
    AckResponse = 'Ack_response',
    Feedback = 'Feedback',
    RobotState = 'Robot_state',
    ReportState = 'Report_state',
    CommandFinished = 'Command_finished'
}

export enum Status {
    Ok = 'Ok',
    Error = 'Error'
}

export type ResponseMessage = AckResponseMessage | FeedbackMessage | RobotStateMessage | ReportStateMessage | CommandFinishedMessage

export type AckResponseMessageData = {
    id: number,
    status: Status,
    command: string,
    message: string
}

export type FeedbackMessageData = {
    id: number,
    message: string
}

export type TCPInformation = {
    pose: [number, number, number, number, number, number],
    speed: [number, number, number, number, number, number],
    force: [number, number, number, number, number, number]
}

export type RobotStateMessageData = {
    safety_status: string,
    runtime_state: string,
    robot_mode: string,
    joints: [number, number, number, number, number, number],
    tcp: TCPInformation,
    payload: number
    digital_out: [boolean, boolean, boolean, boolean, boolean, boolean, boolean, boolean]
}

export type VariableType = 'String' | 'Integer' | 'Float' | 'Boolean' | 'List' | 'Pose'

export type URDataType = string | number | boolean | any[] | [number, number, number, number, number, number]

export type VariableObject = {
    name: string,
    type: VariableType,
    value: URDataType
}

export type stateMessageTypes = string | number | [number, number, number, number, number, number] | TCPInformation | [boolean, boolean, boolean, boolean, boolean, boolean, boolean, boolean] | boolean

export type CommandFinishedMessageData = {
    id: number,
    command: string
}

export type AckResponseMessage = {
    type: ResponseMessageType.AckResponse,
    data: AckResponseMessageData
}

export type FeedbackMessage = {
    type: ResponseMessageType.Feedback,
    data: FeedbackMessageData
}

export type RobotStateMessage = {
    type: ResponseMessageType.RobotState,
    data: RobotStateMessageData
}

export type CommandFinishedMessage = {
    type: ResponseMessageType.CommandFinished,
    data: CommandFinishedMessageData
}

/**
 * The id corresponds to the inspectionPoint id, where this was emitted from.
 */
export type ReportStateMessage = {
    type: ResponseMessageType.ReportState,
    data: VariableObject[],
    id: number
}