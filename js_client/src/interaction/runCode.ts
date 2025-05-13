import {CommandEnteredEvent} from "./EventList";
import { editor } from "../monacoExperiment";
import * as monaco from "monaco-editor";
import { switchButtonStates } from "./buttonHelper";

let current_id: number = 0;

function sendCommand(command: string): void {
    if (command === '') return;
    const customEvent: CommandEnteredEvent = new CommandEnteredEvent({
        text: command,
        id: current_id++,
    });
    document.dispatchEvent(customEvent);
}

document.getElementById('runEditorContentButton')?.addEventListener('click', function () {
    switchButtonStates(true); // For instant feedback
    
    const command = editor.getValue();
    console.log(`Command: ${command}`);
    if (command === '') return;
    sendCommand(command);

    localStorage.setItem('urscript', command);
});

