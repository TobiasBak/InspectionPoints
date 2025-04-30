import {parseMessage} from "./responseMessages/responseMessageParsing";
import {ResponseMessage, ResponseMessageType} from "./responseMessages/responseMessageDefinitions";
import {handleAckResponseMessage} from "./responseMessages/AckResponseHandler";
import {handleFeedbackMessage} from "./responseMessages/FeedbackMessageHandler";
import {handleRobotStateMessage} from "./responseMessages/RobotStateMessageHandler";
import {BeginDebugEvent, CommandEnteredEvent, EventList} from "./interaction/EventList";
import {createCommandMessage, createDebugMessage, createInspectionPointFormat} from "./userMessages/userMessageFactory";
import {InspectionPointFormat, UserMessage} from "./userMessages/userMessageDefinitions";
import {handleCommandFinishedMessage} from "./responseMessages/MessageFinishedHandler";
import {handleReportStateMessage} from "./responseMessages/ReportStateMessageHandler";

/**
 * This is the time in milliseconds that the client will wait between attempting to reconnect to the server after losing connection.
 */
const timeoutSleepTime = 1000;


function get_socket(ip: string, port: number) {
    const out = new WebSocket(
        `ws://${ip}:${port}`
    );

    out.onmessage = (event) => {
        const response = parseMessage(event.data);
        handleMessageFromProxyServer(response);
    }

    return out
}

function handleMessageFromProxyServer(message: ResponseMessage) {
    // console.log("Message from proxy server:", message);
    switch (message.type) {
        case ResponseMessageType.AckResponse:
            handleAckResponseMessage(message);
            break;
        case ResponseMessageType.Feedback:
            handleFeedbackMessage(message);
            break;
        case ResponseMessageType.RobotState:
            handleRobotStateMessage(message);
            break;
        case ResponseMessageType.CommandFinished:
            handleCommandFinishedMessage(message);
            break;
        case ResponseMessageType.ReportState:
            handleReportStateMessage(message);
            break;
        default:
            break;
    }
}

/**
 *
 * @param socket {WebSocket}
 * @param message {UserMessage}
 */
function send(socket: WebSocket, message: UserMessage) {
    if (socket.readyState === WebSocket.CLOSED) {
        return;
    }

    socket.send(JSON.stringify(message));
}

async function testCommands() {
    const proxyServer = get_socket("localhost", 8767);

    const sendCommandToServer = function (e: CommandEnteredEvent) {
        const commandMessage = createCommandMessage(e.detail.id, e.detail.text);
        send(proxyServer, commandMessage)
    };

    const sendDebugCommandToServer = function (e: BeginDebugEvent) {
        const inspectionPoints: InspectionPointFormat[] = []
        e.detail.inspectionPoints.forEach(point =>
            inspectionPoints.push(createInspectionPointFormat(point.id, point.lineNumber, point.command)));
        const debugCommand = createDebugMessage(e.detail.script, inspectionPoints);
        send(proxyServer, debugCommand);
    };


    proxyServer.onopen = () => {
        document.addEventListener(EventList.CommandEntered, sendCommandToServer);
        document.addEventListener(EventList.BeginDebug, sendDebugCommandToServer);
    };

    proxyServer.onclose = () => {
        console.log(`Connection closed. Starting a new connection in ${timeoutSleepTime}ms...`);
        document.removeEventListener(EventList.CommandEntered, sendCommandToServer);
        document.removeEventListener(EventList.BeginDebug, sendDebugCommandToServer);
        setTimeout(() => {
            testCommands().then();
        }, timeoutSleepTime);
    }
}

testCommands().then();

