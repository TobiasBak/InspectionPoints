import {
    ResponseMessage,
    ResponseMessageType,
    stateMessageTypes, VariableObject
} from "./responseMessageDefinitions";


export function handleReportStateMessage(message: ResponseMessage): void {
    if (message.type !== ResponseMessageType.ReportState) {
        throw new Error(`Invalid message type: ${message.type}`);
    }

    iterateMessageData(message.data);
}

function iterateMessageData(data: VariableObject[]): void {
    const id: 'codeVariableDisplay' = "codeVariableDisplay"
    const oldStateVariableView: HTMLElement = document.getElementById(id);
    const codeVariableView: HTMLElement = document.createElement('div');
    codeVariableView.id = id;

    data.forEach((variable): void => {
        generateHtmlFromMessageData(variable.name, codeVariableView, variable.value)
    });

    if (oldStateVariableView) {
        oldStateVariableView.replaceWith(codeVariableView);
    } else {
        document.getElementById('stateVariables').appendChild(codeVariableView);
    }
}

function generateHtmlFromMessageData(messageDataKey: string, stateVariableView: HTMLElement, messageDataValue:any): void {

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

function prettyPrint(information: stateMessageTypes): string {
    if (typeof information === 'string') {
        return information;
    }
    if (typeof information === 'number') {
        return information.toString();
    }
    if (Array.isArray(information)) {
        return information.join(', ');
    }
    if (typeof information === 'object') {
        return JSON.stringify(information);
    }
}