import {ReportStateMessage, URDataType, VariableObject} from "./responseMessageDefinitions";
import {BeginDebugEvent, EventList} from "../interaction/EventList";


let storage: ReportStateMessage[] = [];

const coldStorage: Map<number, ReportStateMessage[]> = new Map<number, ReportStateMessage[]>();
let currentId: number = 0;

document.addEventListener(EventList.BeginDebug, (event: BeginDebugEvent) => {
    coldStorage.set(currentId, storage);
    currentId++
    storage = [];
})

/**
 * Get the stored messages in the received order.
 * @param forIds {Set<number>} - The ids of the messages to return. If undefined, return all messages.
 */
export function getStoredMessages(forIds: Set<number> = undefined): ReportStateMessage[] {
    if (forIds === undefined) {
        return storage;
    }

    return storage.filter((message: ReportStateMessage) => forIds.has(message.id));
}

export function storeMessage(message: ReportStateMessage): void {
    storage.push(message);
}

export function getCurrentId(): number {
    return currentId;
}

/**
 * Map the variable name to the section element that stores it.
 */
const sectionStorage = new Map<string, HTMLElement>();

/**
 * Display the message data in the HTML.
 * This function will grey out the sections that are not active in this message, but keep them in the view.
 * @param message {ReportStateMessage} - The message to display variables from.
 */
export function displayMessageData(message: ReportStateMessage): void {
    const data: VariableObject[] = message.data

    const id: 'codeVariableDisplay' = "codeVariableDisplay"
    const codeVariableDisplay: HTMLElement = document.getElementById(id);

    // console.log("Provided_id from last logged report state", message.id)

    sectionStorage.forEach(section => {
        section.classList.add("inactive-section")
    });

    data.forEach((variable): void => {
        const oldSection = sectionStorage.get(variable.name);
        const newSection = generateHtmlFromMessageData(variable.name, variable.value)
        if (oldSection) {
            oldSection.replaceWith(newSection);
        }else{
            codeVariableDisplay.appendChild(newSection);
        }
        sectionStorage.set(variable.name, newSection);
    });
}

function generateHtmlFromMessageData(messageDataKey: string, messageDataValue:URDataType): HTMLElement {
    const stateVariableSection: HTMLElement = document.createElement('section');
    stateVariableSection.classList.add('stateVariableSection', 'flex');

    const sectionColumn45: HTMLDivElement = document.createElement('div');
    sectionColumn45.classList.add('column45');

    const sectionColumn55: HTMLDivElement = document.createElement('div');
    sectionColumn55.classList.add('column55');

    const column45Text: HTMLParagraphElement = document.createElement('p');
    column45Text.textContent = messageDataKey;

    const column55Text: HTMLParagraphElement = document.createElement('p');
    if (Array.isArray(messageDataValue)) {
        for (let i = 0; i < messageDataValue.length; i++) {
            column55Text.appendChild(document.createTextNode("[" + (i) + "]: " + prettyPrint(messageDataValue[i])));
            column55Text.appendChild(document.createElement('br'));
        }
    }else{
        column55Text.textContent = prettyPrint(messageDataValue);
    }

    sectionColumn45.appendChild(column45Text);
    sectionColumn55.appendChild(column55Text);
    stateVariableSection.appendChild(sectionColumn45);
    stateVariableSection.appendChild(sectionColumn55);
    return stateVariableSection
}

function prettyPrint(information: URDataType): string {
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
    if (typeof information === 'boolean') {
        return information ? 'True' : 'False';
    }
}