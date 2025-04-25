import {CommandEnteredDetail, CommandEnteredEvent, EventList} from "./interaction/EventList";
import { editor } from "./monacoExperiment";

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
    const command = editor.getValue();
    console.log(`Command: ${command}`);
    if (command === '') return;
    sendCommand(command);
});

document.body.addEventListener('keydown', function (e: KeyboardEvent): void {
    switch (e.key) {
        case "1":
            if (e.ctrlKey) {
                e.preventDefault();
                sendCommand("movej(p[-0.421, -0.436, 0.1, 2.61, -1.806, -0.019], a=0.3, v=0.3)");
            }
            break;
        case "2":
            if (e.ctrlKey) {
                e.preventDefault();
                sendCommand("movej(p[-0.194, -0.6, 0.066, 2.61, -1.806, -0.019], a=0.3, v=0.3)");
            }
            break;
        case "3":
            if (e.ctrlKey) {
                e.preventDefault();
                sendCommand("movej(p[-0.194, -0.6, 0.066, 2.61, -1.806, -0.019], a=0.05, v=0.05)");
            }
            break;
        case "4":
            if (e.ctrlKey) {
                e.preventDefault();
                sendCommand("movej(p[-0.194, -0.6, 0.066, 2.61, -1.806, -0.019], a=0.05, v=0.05)");
            }
            break;

    }
})
