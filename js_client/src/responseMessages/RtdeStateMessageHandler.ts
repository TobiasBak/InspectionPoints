import {
    ResponseMessage,
    ResponseMessageType,
    RtdeStateMessage,
} from "./responseMessageDefinitions";



export function handleRtdeStateMessage(message: ResponseMessage): void {
    if (message.type !== ResponseMessageType.RtdeState) {
        throw new Error(`Invalid message type: ${message.type}`);
    }

    handlePlayingState(message);
    showRobotReady(message);
    showSafetyStatus(message);
}


let currentSafetyStatus: string = '';
const safetyStatusDisplay: HTMLElement | null = document.getElementById('safetyStatusDisplay');

function showSafetyStatus(rtdeState: RtdeStateMessage): void {
    const safetyStatus = rtdeState.data.safety_status;

    if (!safetyStatusDisplay) {
        console.error('Safety status display element not found');
        return;
    }

    if (safetyStatus === currentSafetyStatus) {
        return;
    }

    const greenStates: Set<string> = new Set([
        'normal_mode',
    ]);

    const yellowStates: Set<string> = new Set([
        'reduced_mode',
    ]);


    safetyStatusDisplay.children[0].classList.add('hidden')
    safetyStatusDisplay.children[1].classList.add('hidden')
    safetyStatusDisplay.children[2].classList.add('hidden')

    if (greenStates.has(safetyStatus)) {
        safetyStatusDisplay.children[2].classList.remove('hidden');
    }else if (yellowStates.has(safetyStatus)) {
        safetyStatusDisplay.children[0].classList.remove('hidden');
    } else {
        safetyStatusDisplay.children[1].classList.remove('hidden');
    }
}

let currentRobotMode: string = '';
const robotModeDisplay: HTMLElement | null = document.getElementById('readyDisplay');

function showRobotReady(rtdeState: RtdeStateMessage): void {
    const robotMode = rtdeState.data.robot_mode;

    if (robotMode === currentRobotMode) {
        return;
    }

    currentRobotMode = robotMode;
    if (!robotModeDisplay) {
        console.error('Robot mode display element not found');
        return;
    }

    robotModeDisplay.classList.remove('readiness-red');
    robotModeDisplay.classList.remove('readiness-ready');
    robotModeDisplay.classList.remove('readiness-yellow');

    const redStates: Set<string> = new Set([
        'no_controller',
        'disconnected',
        'confirm_safety',
        'power_off',
        'idle',
        'backdrive',
    ]);

    if (robotMode === 'running') {
        robotModeDisplay.classList.add('readiness-ready');
    } else if (robotMode === 'power_on' || robotMode === 'booting' || robotMode === 'updating_firmware') {
        robotModeDisplay.classList.add('readiness-yellow');
    } else if (redStates.has(robotMode)) {
        robotModeDisplay.classList.add('readiness-red');
    }
}

const spinner: HTMLElement | null = document.getElementById('spinner');
let spinnerState: boolean = false;


function handlePlayingState(rtdeState: RtdeStateMessage): void{
    const program_state = rtdeState.data.runtime_state;
    let newState = false;

    if (program_state === 'playing' || program_state === 'resuming') {
        newState = true;
    }
    switchPlayState(newState);

    if (newState !== spinnerState) {
        spinnerState = newState;
        switchPlayState(spinnerState);
    }
}

const spinnerStateChangeCallbacks: ((enabled: boolean) => void)[] = [];

export function registerForSpinnerStateChange(callback: (enabled: boolean) => void): void {
    spinnerStateChangeCallbacks.push(callback);
}

function switchPlayState(enabled: boolean): void {
    if (enabled === spinnerState) {
        return;
    }
    spinnerState = enabled;
    spinnerStateChangeCallbacks.forEach(callback => callback(enabled));

    if (!spinner) {
        console.error('Spinner element not found');
        return;
    }
    if (enabled) {
        spinner.classList.remove('hidden-visibility');
    } else {
        spinner.classList.add('hidden-visibility');
    }
}