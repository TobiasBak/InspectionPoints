import {
    AckResponseMessage,
    FeedbackMessage, ReportStateMessage,
    ResponseMessage,
    ResponseMessageType,
    RtdeStateMessage,
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
            return parseRtdeStateMessage(parsed);
        case "Report_state":
            return parseReportStateMessage(parsed);
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

function parseRtdeStateMessage(message: any): RtdeStateMessage {
    if (message.type !== "Robot_state") {
        throw new Error(`Invalid message type: ${message.type}`);
    }
    return {
        type: ResponseMessageType.RtdeState,
        data: {
            safety_status: noneGuard(message.data.safety_status),
            runtime_state: noneGuard(message.data.runtime_state),
            robot_mode: noneGuard(message.data.robot_mode)
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
        })],
        id: noneGuard(message.id),
        timestamp: noneGuard(message.timestamp),
    };
}
