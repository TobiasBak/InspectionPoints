import {CommandFinishedMessage, ResponseMessage, ResponseMessageType} from "./responseMessageDefinitions";
import {CommandFinishedEvent, EventList} from "../interaction/EventList";

export function handleCommandFinishedMessage(message: ResponseMessage): void {
    if (message.type !== ResponseMessageType.CommandFinished) {
        throw new Error(`Invalid message type: ${message.type}`);
    }

    emitCommandFinishedEvent(message);
}

export function emitCommandFinishedEvent(message: ResponseMessage): void {
    if (message.type !== ResponseMessageType.CommandFinished) {
        return;
    }
    const message_copy: CommandFinishedMessage = <CommandFinishedMessage>message;
    const event = new CommandFinishedEvent({
            command: message_copy.data.command,
            id: message_copy.data.id
    });
    document.dispatchEvent(event);
}