import { switchButtonStates } from "./buttonHelper";
import { StopProgramEvent } from "./EventList";

function stopProgram(): void {
    const customEvent: StopProgramEvent = new StopProgramEvent({
        text: 'STOP_PROGRAM',
        id: Date.now(), 
    });
    document.dispatchEvent(customEvent);
}

document.getElementById('stopProgramButton')?.addEventListener('click', function () {
    console.log('Stop Program button clicked.');
    if (!document.getElementById('stopProgramButton')) {
        console.error('Stop Program button not found.');
        return;
    }
    switchButtonStates(); // For instant feedback
    stopProgram();
});
