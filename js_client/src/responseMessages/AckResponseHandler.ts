import {ResponseMessage, ResponseMessageType} from "./responseMessageDefinitions";
import {getChildWithClass, getCommandEntry} from "../Toolbox/DomTools";

const errorClass = "error-response"
const successClass = "success-response"

const frontend_text_for_ack_success = "Command accepted by robot"

export function handleAckResponseMessage(message: ResponseMessage): void {
    if (message.type !== ResponseMessageType.AckResponse) {
        console.log('not an Ack_response message: ', message);
        return
    }

    const commandWrapper: HTMLElement = getCommandEntry(message.data.id);
    if (!commandWrapper) {
        console.log(`no command with id: ${message.data.id}`, message);
        return
    }
    const contentWrapper: HTMLElement = getChildWithClass(commandWrapper, 'contentWrapper');
    const responseWrapper: HTMLElement = getChildWithClass(contentWrapper, 'responseWrapper');

    const responseParagraph: HTMLParagraphElement = document.createElement('p');
    responseParagraph.classList.add("response");

    if (message.data.status !== 'Ok') {
        const messageParts = message.data.message.split(':')
        const statusType = `<span>${messageParts.shift()}:</span>`
        responseParagraph.classList.add(errorClass);

        responseParagraph.innerHTML = statusType + messageParts.join(':');
    } else {
        responseParagraph.innerHTML = frontend_text_for_ack_success
    }


    responseWrapper.appendChild(responseParagraph);

    console.log(message);
}