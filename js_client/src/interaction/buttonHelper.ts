import {registerForSpinnerStateChange} from "../responseMessages/RtdeStateMessageHandler";

const stopButton: HTMLButtonElement | null = document.getElementById('stopProgramButton') as HTMLButtonElement;
const debugButton: HTMLButtonElement | null = document.getElementById('debugEditorButton') as HTMLButtonElement;
const startButton: HTMLButtonElement | null = document.getElementById('runEditorContentButton') as HTMLButtonElement;

function isButtonDisabled(button: HTMLButtonElement | null): boolean {
    console.log('Button: ', button, 'Disabled: ', button?.disabled);
    if (button) {
        return button.disabled;
    } else {
        console.error('Button not found');
        return false;
    }
}


function setButtonDisabled(button: HTMLButtonElement | null, state: boolean): void {
    if (button) {
        button.disabled = state;
    } else {
        console.error('Button not found');
    }
    console.log('Button state set to:', state);
}


/**
 * @param playing - True if the program is switching to playing, false if it is not.
 */
export function switchButtonStates(playing: boolean): void {
    setButtonDisabled(startButton, playing);
    setButtonDisabled(debugButton, playing);
    setButtonDisabled(stopButton, !playing);
}

registerForSpinnerStateChange((enabled: boolean) => {
    switchButtonStates(enabled);
})