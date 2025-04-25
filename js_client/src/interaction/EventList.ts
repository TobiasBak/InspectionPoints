
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

export type BeginDebugDetail = {
    script: string[],
    inspectionPoints: {
        id: number,
        lineNumber: number,
        command: string,
    }[],
}

export class BeginDebugEvent extends CustomEvent<BeginDebugDetail> {
    constructor(detail: BeginDebugDetail) {
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