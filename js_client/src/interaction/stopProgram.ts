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
    stopProgram();
});

export function setStopButtonDisabled(state: boolean): void {
    const stopButton: HTMLButtonElement | null = document.getElementById('stopProgramButton') as HTMLButtonElement;
    if (stopButton) {
        stopButton.disabled = !state;
    } else {
        console.error('Stop button not found');
    }
    console.log('Stop button state set to:', state);
}

export function isStopButtonDisabled(): boolean {
    const stopButton: HTMLButtonElement | null = document.getElementById('stopProgramButton') as HTMLButtonElement;
    if (stopButton) {
        return stopButton.disabled;
    } else {
        console.error('Stop button not found');
        return false;
    }
}