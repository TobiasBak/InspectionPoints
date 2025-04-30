import {
    AckResponseMessage, CommandFinishedMessage,
    FeedbackMessage, ReportStateMessage,
    ResponseMessage,
    ResponseMessageType,
    RobotStateMessage,
    Status, VariableObject
} from "./responseMessageDefinitions";

export function parseMessage(message: string): ResponseMessage {
    const parsed = JSON.parse(message);

    switch (parsed.type) {
        case "Ack_response":
            return parseAckResponseMessage(parsed);
        case "Feedback":
            return parseFeedbackMessage(parsed);
        case "Robot_state":
            return parseRobotStateMessage(parsed);
        case "Report_state":
            return parseReportStateMessage(parsed);
            break;
        case "Command_finished":
            return parseCommandFinishedMessage(parsed);
        default:
            throw new Error(`Invalid message type: ${parsed.type}`);
    }
}

function parseStatus(status: string): Status {
    if (!(status in Status)) {
        throw new Error(`Invalid status: ${status}`);
    }
    return status === "Ok" ? Status.Ok : Status.Error;
}

function parseAckResponseMessage(message: any): AckResponseMessage {
    if (message.type !== "Ack_response") {
        throw new Error(`Invalid message type: ${message.type}`);
    }
    return {
        type: ResponseMessageType.AckResponse,
        data: {
            id: noneGuard(message.data.id),
            status: parseStatus(message.data.status),
            command: noneGuard(message.data.command),
            message: noneGuard(message.data.message)
        }
    };
}

function parseFeedbackMessage(message: any): FeedbackMessage {
    if (message.type !== "Feedback") {
        throw new Error(`Invalid message type: ${message.type}`);
    }
    return {
        type: ResponseMessageType.Feedback,
        data: {
            id: noneGuard(message.data.id),
            message: noneGuard(message.data.message)
        }
    };
}

function noneGuard(value: any): any {
    if (value === null || value === undefined) {
        throw new Error("Unexpected null or undefined value");
    }
    return value;
}

function parseRobotStateMessage(message: any): RobotStateMessage {
    if (message.type !== "Robot_state") {
        throw new Error(`Invalid message type: ${message.type}`);
    }
    return {
        type: ResponseMessageType.RobotState,
        data: {
            safety_status: noneGuard(message.data.safety_status),
            runtime_state: noneGuard(message.data.runtime_state),
            robot_mode: noneGuard(message.data.robot_mode),
            joints: noneGuard(message.data.joints),
            tcp: {
                pose: noneGuard(message.data.tcp.pose),
                speed: noneGuard(message.data.tcp.speed),
                force: noneGuard(message.data.tcp.force)
            },
            payload: noneGuard(message.data.payload),
            digital_out: [noneGuard(message.data.digital_out_0), noneGuard(message.data.digital_out_1), noneGuard(message.data.digital_out_2), noneGuard(message.data.digital_out_3), noneGuard(message.data.digital_out_4), noneGuard(message.data.digital_out_5), noneGuard(message.data.digital_out_6), noneGuard(message.data.digital_out_7)],
        }
    };
}

function parseReportStateMessage(message: any): ReportStateMessage {
    if (message.type !== "Report_state") {
        throw new Error(`Invalid message type: ${message.type}`);
    }
    return {
        type: ResponseMessageType.ReportState,
        data: [...message.data.map((variable: any) => {
            return {
                name: noneGuard(variable.name),
                type: noneGuard(variable.type),
                value: noneGuard(variable.value)
            };
        })]
    };
}


function parseCommandFinishedMessage(message: any): CommandFinishedMessage {
    if (message.type !== "Command_finished") {
        throw new Error(`Invalid message type: ${message.type}`);
    }
    return {
        type: ResponseMessageType.CommandFinished,
        data: {
            id: noneGuard(message.data.id),
            command: noneGuard(message.data.command)
        }
    };
}