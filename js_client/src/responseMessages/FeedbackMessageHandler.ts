import {ResponseMessage, ResponseMessageType} from "./responseMessageDefinitions";

export function handleFeedbackMessage(message: ResponseMessage): void {
    if (message.type !== ResponseMessageType.Feedback) {
        throw new Error(`Invalid message type: ${message.type}`);
    }
    
    throw new Error('Feedback message handler not implemented');
}