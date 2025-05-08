import {generateVariableSelection, listOfVariablesToDisplay} from "../cobotVariableSelection";
import { isStopButtonDisabled, setStopButtonDisabled } from "../interaction/stopProgram";
import {
    ResponseMessage,
    ResponseMessageType,
    RtdeStateMessage,
    RtdeStateMessageData, rtdeStateMessageType
} from "./responseMessageDefinitions";


let lastRtdeStateMessage: RtdeStateMessage;

export function handleRtdeStateMessage(message: ResponseMessage): void {
    if (message.type !== ResponseMessageType.RtdeState) {
        throw new Error(`Invalid message type: ${message.type}`);
    }

    lastRtdeStateMessage = message;
    switchStopButtonState(message);
    handleSpinnerState(message);
    showRobotReady(message);
    showSafetyStatus(message);

    generateVariableSelection(message.data, replayRtdeStateMessage);
    // iterateMessageData(message.data);
}

function switchStopButtonState(rtdeState: RtdeStateMessage): void {
    const program_state = rtdeState.data.runtime_state;
    console.log('program_state', program_state);
    if (program_state === 'playing' && isStopButtonDisabled() === true) {
        setStopButtonDisabled(true);
    } else if (program_state === 'stopped' && isStopButtonDisabled() === false) {
        setStopButtonDisabled(false);
    }
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


function handleSpinnerState(rtdeState: RtdeStateMessage): void{
    const program_state = rtdeState.data.runtime_state;
    let newState = false;

    if (program_state === 'playing' || program_state === 'resuming') {
        newState = true;
    }
    switchSpinnerState(newState);

    if (newState !== spinnerState) {
        spinnerState = newState;
        switchSpinnerState(spinnerState);
    }
}

function switchSpinnerState(enabled: boolean): void {
    if (enabled === spinnerState) {
        return;
    }
    spinnerState = enabled;

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
    

function replayRtdeStateMessage(): void {
    if (lastRtdeStateMessage) {
        handleRtdeStateMessage(lastRtdeStateMessage);
    }
}

function iterateMessageData(data: RtdeStateMessageData): void {
    const id: 'stateVariableDisplay' = "stateVariableDisplay"
    const oldStateVariableView: HTMLElement = document.getElementById(id);
    const stateVariableView: HTMLElement = document.createElement('div');
    stateVariableView.id = id;

    Object.entries(data).forEach(([key, value]): void => {
        if (listOfVariablesToDisplay().includes(key)) {
            generateHtmlFromMessageData(key, stateVariableView, value);
        }
    });

    if (oldStateVariableView) {
        oldStateVariableView.replaceWith(stateVariableView);
    } else {
        document.getElementById('stateVariables').appendChild(stateVariableView);
    }
}

function generateHtmlFromMessageData(messageDataKey: string, stateVariableView: HTMLElement, messageDataValue: rtdeStateMessageType): void {

    const stateVariableSection: HTMLElement = document.createElement('section');
    stateVariableSection.classList.add('stateVariableSection', 'flex');

    const sectionColumn45: HTMLDivElement = document.createElement('div');
    sectionColumn45.classList.add('column45');

    const sectionColumn55: HTMLDivElement = document.createElement('div');
    sectionColumn55.classList.add('column55');

    const column45Text: HTMLParagraphElement = document.createElement('p');
    column45Text.textContent = messageDataKey;

    const column55Text: HTMLParagraphElement = document.createElement('p');
    column55Text.textContent = prettyPrint(messageDataValue);
    
    sectionColumn45.appendChild(column45Text);
    sectionColumn55.appendChild(column55Text);
    stateVariableSection.appendChild(sectionColumn45);
    stateVariableSection.appendChild(sectionColumn55);
    stateVariableView.appendChild(stateVariableSection);
}

function prettyPrint(information: rtdeStateMessageType): string {
    if (typeof information === 'string') {
        return information;
    }
}