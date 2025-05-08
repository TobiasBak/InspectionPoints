import {
    ReportStateMessage,
    ResponseMessage,
    ResponseMessageType,
    URDataType,
    VariableObject,
    VariableType
} from "./responseMessageDefinitions";


/***
 * The public method to handle the ReportStateMessage are.
 * ReportStateMessageHandler.getStoredMessages()
 *
 * ReportStateMessageHandler.displayMessageData()
 *
 * Use getStoredMessages() to get the stored messages first.
 * Then use displayMessageData() to display the messages that you want.
 * It will handle greying out the sections that are not currently displayed.
 */


const storage: ReportStateMessage[] = [];

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

export function handleReportStateMessage(message: ResponseMessage): void {
    if (message.type !== ResponseMessageType.ReportState) {
        throw new Error(`Invalid message type: ${message.type}`);
    }

    console.log(`Received message:`, message);

    message.data.forEach((variable: VariableObject) => {
      if (typeof variable.value === 'string'){
        variable.value = parseStringContent(variable.value);
        variable.type = checkNewType(variable.value);
      }
    })

    storage.push(message);

    displayMessageData(message);
}


function parseStringContent(message: string): URDataType {
    return ensureType(rawParseStringContent(message));
}

function checkNewType(data: URDataType): VariableType {
    if (typeof data === 'string') {
        return "String";
    }
    if (typeof data === 'number') {
        return "Float";
    }
    if (typeof data === 'boolean') {
        return "Boolean";
    }
    if (Array.isArray(data)) {
        return "List";
    }

    throw new Error(`Unsupported type: ${typeof data} - ${data}`);
}

function rawParseStringContent(message: string) {
    try {
        return JSON.parse(message);
    }catch (error){
        if (!(error instanceof SyntaxError)) {
            throw error;
        }
        return message;
    }
}

function ensureType(input: any): URDataType{
    if (typeof input === 'string' ||typeof input === 'number' || typeof input === 'boolean') {
        return input;
    }
    if (Array.isArray(input)) {
        return input.map(item => ensureType(item));
    }
    throw new Error(`Unsupported type: ${typeof input} - ${input}`);
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

    const cobotStateDisplay: HTMLElement = document.getElementById("stateVariableDisplay");
    const codeVariableDisplay: HTMLElement = document.getElementById("codeVariableDisplay");

    // console.log("Provided_id from last logged report state", message.id)

    sectionStorage.forEach(section => {
        section.classList.add("inactive-section")
    });

    data.forEach((variable): void => {
        const targetSection = variable.global ? cobotStateDisplay : codeVariableDisplay;

        const oldSection = sectionStorage.get(variable.name);
        const newSection = generateHtmlFromMessageData(variable.name, variable.value)
        if (oldSection) {
            oldSection.replaceWith(newSection);
        }else{
            targetSection.appendChild(newSection);
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