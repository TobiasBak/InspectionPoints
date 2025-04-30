import {InspectionPointMessageData} from "../userMessages/userMessageDefinitions";

export enum EventList {
    CommandEntered = "commandEntered",
    CommandFinished = "commandFinished",
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

export type CommandFinishedDetail = {
    command: string,
    id: number,
}

export class CommandFinishedEvent extends CustomEvent<CommandFinishedDetail> {
    constructor(detail: CommandFinishedDetail) {
        super(EventList.CommandFinished, { detail });
    }
}