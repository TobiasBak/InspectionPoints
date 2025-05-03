import {listOfVariablesToDisplay} from "../cobotVariableSelection";
import {
    ResponseMessage,
    ResponseMessageType,
    RtdeStateMessage,
    RtdeStateMessageData, rtdeStateMessageType
} from "./responseMessageDefinitions";


let lastRtdeStateMessage: RtdeStateMessage;

export function handleRtdeStateMessage(message: ResponseMessage): void {
    if (message.type !== ResponseMessageType.RtdeState) {
        throw new Error(`Invalid message type: ${message.type}`);
    }

    lastRtdeStateMessage = message;

    iterateMessageData(message.data);
}


function iterateMessageData(data: RtdeStateMessageData): void {
    const id: 'statusVariableDisplay' = "statusVariableDisplay"
    const oldStateVariableView: HTMLElement = document.getElementById(id);
    const stateVariableView: HTMLElement = document.createElement('div');
    stateVariableView.id = id;

    Object.entries(data).forEach(([key, value]): void => {
        if (listOfVariablesToDisplay().includes(key)) {
            generateHtmlFromMessageData(key, stateVariableView, value);
        }
    });

    if (oldStateVariableView) {
        oldStateVariableView.replaceWith(stateVariableView);
    } else {
        document.getElementById('stateVariables').appendChild(stateVariableView);
    }
}

function generateHtmlFromMessageData(messageDataKey: string, stateVariableView: HTMLElement, messageDataValue: rtdeStateMessageType): void {

    const stateVariableSection: HTMLElement = document.createElement('section');
    stateVariableSection.classList.add('stateVariableSection', 'flex');

    const sectionColumn45: HTMLDivElement = document.createElement('div');
    sectionColumn45.classList.add('column45');

    const sectionColumn55: HTMLDivElement = document.createElement('div');
    sectionColumn55.classList.add('column55');

    const column45Text: HTMLParagraphElement = document.createElement('p');
    column45Text.textContent = messageDataKey;

    const column55Text: HTMLParagraphElement = document.createElement('p');
    column55Text.textContent = prettyPrint(messageDataValue);
    
    sectionColumn45.appendChild(column45Text);
    sectionColumn55.appendChild(column55Text);
    stateVariableSection.appendChild(sectionColumn45);
    stateVariableSection.appendChild(sectionColumn55);
    stateVariableView.appendChild(stateVariableSection);
}

function prettyPrint(information: rtdeStateMessageType): string {
    if (typeof information === 'string') {
        return information;
    }
}