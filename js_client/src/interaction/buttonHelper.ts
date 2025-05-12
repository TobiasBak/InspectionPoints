
function isButtonDisabled(button: HTMLButtonElement | null): boolean {
    console.log('Button: ', button, 'Disabled: ', button?.disabled);
    if (button) {
        return button.disabled;
    } else {
        console.error('Button not found');
        return false;
    }
}

export function isStopButtonDisabled(): boolean {
    const stopButton: HTMLButtonElement | null = document.getElementById('stopProgramButton') as HTMLButtonElement;
    return isButtonDisabled(stopButton);
}

export function isStartButtonDisabled(): boolean {
    const startButton: HTMLButtonElement | null = document.getElementById('runEditorContentButton') as HTMLButtonElement;
    return isButtonDisabled(startButton);
}

export function isDebugButtonDisabled(): boolean {
    const debugButton: HTMLButtonElement | null = document.getElementById('debugEditorButton') as HTMLButtonElement;
    return isButtonDisabled(debugButton);
}
function setButtonDisabled(button: HTMLButtonElement | null, state: boolean): void {
    if (button) {
        button.disabled = state;
    } else {
        console.error('Button not found');
    }
    console.log('Button state set to:', state);
}

export function setStartButtonDisabled(state: boolean): void {
    const startButton: HTMLButtonElement | null = document.getElementById('runEditorContentButton') as HTMLButtonElement;
    setButtonDisabled(startButton, state);
}
/**
 * Disable or enable the stop button.
 * @param state - True to enable the button, false to disable it.
 */

export function setStopButtonDisabled(state: boolean): void {
    const stopButton: HTMLButtonElement | null = document.getElementById('stopProgramButton') as HTMLButtonElement;
    setButtonDisabled(stopButton, state);
}

export function setDebugButtonDisabled(state: boolean): void {
    const debugButton: HTMLButtonElement | null = document.getElementById('debugEditorButton') as HTMLButtonElement;
    setButtonDisabled(debugButton, state);
}

export function switchButtonStates(): void {
    if (isStopButtonDisabled()) {
        setStartButtonDisabled(true);
        setDebugButtonDisabled(true);
        setStopButtonDisabled(false);
    } else {
        setStartButtonDisabled(false);
        setDebugButtonDisabled(false);
        setStopButtonDisabled(true);
    }
}
