import {generateVariableSelection, listOfVariablesToDisplay} from "../cobotVariableSelection";
import { isStopButtonDisabled, setStopButtonDisabled } from "../interaction/stopProgram";
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
    switchStopButtonState(message);

    generateVariableSelection(message.data, replayRtdeStateMessage);
    iterateMessageData(message.data);
}

function switchStopButtonState(rtdeState: RtdeStateMessage): void {
    const program_state = rtdeState.data.runtime_state;
    console.log('program_state', program_state);
    if (program_state === 'playing' && isStopButtonDisabled() === true) {
        setStopButtonDisabled(true);
    } else if (program_state === 'stopped' && isStopButtonDisabled() === false) {
        setStopButtonDisabled(false);
    }
}
    

function replayRtdeStateMessage(): void {
    if (lastRtdeStateMessage) {
        handleRtdeStateMessage(lastRtdeStateMessage);
    }
}

function iterateMessageData(data: RtdeStateMessageData): void {
    const id: 'stateVariableDisplay' = "stateVariableDisplay"
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