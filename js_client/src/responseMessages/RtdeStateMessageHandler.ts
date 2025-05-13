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

    let tooltipContent = '';

    if (greenStates.has(safetyStatus)) {
        safetyStatusDisplay.children[2].classList.remove('hidden');
        tooltipContent = 'The cobot is operating normally.';
    }else if (yellowStates.has(safetyStatus)) {
        safetyStatusDisplay.children[0].classList.remove('hidden');
        tooltipContent = 'The cobot is operating in reduced mode.';
    } else {
        safetyStatusDisplay.children[1].classList.remove('hidden');
        tooltipContent = 'The cobot has stopped due to a safety issue.';
    }

    // Tooltip handling
    const tooltipId = 'safetyStatusTooltip';
    setupTooltip(safetyStatusDisplay, tooltipId, tooltipContent);
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

    let tooltipContent = '';

    if (robotMode === 'running') {
        robotModeDisplay.classList.add('readiness-ready');
        tooltipContent = 'The cobot is ready to execute programs.';
    } else if (robotMode === 'power_on' || robotMode === 'booting' || robotMode === 'updating_firmware') {
        robotModeDisplay.classList.add('readiness-yellow');
        tooltipContent = 'The cobot is busy (powering on, booting, or updating firmware). Please wait.';
    } else if (redStates.has(robotMode)) {
        robotModeDisplay.classList.add('readiness-red');
        tooltipContent = 'The cobot requires action on the Polyscope interface to continue.';
    }

    // Tooltip handling
    const tooltipId = 'readyStatusTooltip';
    setupTooltip(robotModeDisplay, tooltipId, tooltipContent);
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

function setupTooltip(targetElement: HTMLElement | null, tooltipId: string, content: string): void {
    if (!targetElement) {
        console.error(`Target element not found for  the tooltip: ${tooltipId}`);
        return;
    }

    targetElement.addEventListener('mouseenter', (event) => {
        const tooltip = document.getElementById(tooltipId);
        if (tooltip) {
            tooltip.textContent = content;
            tooltip.classList.add('visible');
            tooltip.classList.remove('hidden');
            positionTooltip(event, tooltipId);
        }
    });

    targetElement.addEventListener('mouseleave', () => {
        const tooltip = document.getElementById(tooltipId);
        if (tooltip) {
            tooltip.classList.remove('visible');
            tooltip.classList.add('hidden');
        }
    });
}

function positionTooltip(event: MouseEvent, tooltipId: string): void {
    const tooltip = document.getElementById(tooltipId);
    const targetElement = event.currentTarget as HTMLElement;

    if (tooltip && targetElement) {
        const targetRectangle = targetElement.getBoundingClientRect();

        // Calculate position to place just below the targeted element
        let left = targetRectangle.left;
        const top = targetRectangle.bottom + 5; // 5px to place it just below the div

        // Get the tooltip width and the viewport width
        const tooltipRect = tooltip.getBoundingClientRect();
        const viewportWidth = window.innerWidth;

        // Ensures the tooltip does not overflow the viewport
        if (left + tooltipRect.width > viewportWidth) {
            left = viewportWidth - tooltipRect.width - 10;
        }

        // Apply the position
        tooltip.style.left = `${left}px`;
        tooltip.style.top = `${top}px`;
    }
}
