import {
    ReportStateMessage,
    ResponseMessage,
    ResponseMessageType,
    URDataType,
    VariableObject,
    VariableType
} from "./responseMessageDefinitions";
import {refreshGraph} from "../inspectionPointGraph/InspectionGraph";
import {displayMessageData, storeMessage} from "./displayReportStateMessage";


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




export function handleReportStateMessage(message: ResponseMessage): void {
    if (message.type !== ResponseMessageType.ReportState) {
        throw new Error(`Invalid message type: ${message.type}`);
    }
    
    message.data.forEach((variable: VariableObject) => {
      if (typeof variable.value === 'string'){
        variable.value = parseStringContent(variable.value);
        variable.type = checkNewType(variable.value);
      }
    })

    storeMessage(message);

    displayMessageData(message);
    refreshGraph().then()
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
