import {ResponseMessage, ResponseMessageType} from "./responseMessageDefinitions";


export function handleReportStateMessage(message: ResponseMessage): void {
    if (message.type !== ResponseMessageType.ReportState) {
        console.log('not a ReportState message: ', message);
        return;
    }
}