import {InspectionPointMessageData} from "../userMessages/userMessageDefinitions";

export enum EventList {
    CommandEntered = "commandEntered",
    CommandAccepted = "commandAccepted",
    CommandRejected = "commandRejected",
    BeginDebug = "beginDebug",
}


export type CommandEnteredDetail = {
    text: string,
    id: number,
}

export class CommandEnteredEvent extends CustomEvent<CommandEnteredDetail> {
    constructor(detail: CommandEnteredDetail) {
        super(EventList.CommandEntered, { detail });
    }
}


export class BeginDebugEvent extends CustomEvent<InspectionPointMessageData> {
    constructor(detail: InspectionPointMessageData) {
        super(EventList.BeginDebug, { detail });
    }
}


