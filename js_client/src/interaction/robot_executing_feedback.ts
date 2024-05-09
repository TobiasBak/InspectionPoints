import {EventList} from "./EventList";
import {getChildWithClass, getCommandEntry} from "../Toolbox/DomTools";
import {createUndoButton} from "../undoEventHandler";
import {statusWrapperClass} from "../commandHistory";

const spinnerWrapperClass: string = "spinnerWrapper"

document.addEventListener(EventList.CommandAccepted, function (e: CustomEvent): void {
    const commandEntry: HTMLElement = getCommandEntry(e.detail.id);
    const statusWrapper: HTMLElement = getChildWithClass(commandEntry, statusWrapperClass);
    if(!statusWrapper) return;
    statusWrapper.appendChild(createExecutingFeedbackSpinner());
});

document.addEventListener(EventList.CommandFinished, function (e: CustomEvent): void {
    stopRobotExecutingFeedback(e.detail.id);
})

document.addEventListener(EventList.UndoEvent, function (e: CustomEvent): void {
    const commandEntry = getCommandEntry(e.detail.id)
    const statusWrapper = getChildWithClass(commandEntry, statusWrapperClass);
    if(!statusWrapper) return;
    statusWrapper.appendChild(createExecutingFeedbackSpinner());
})

function stopRobotExecutingFeedback(id: number): void {
    const commandEntry: HTMLElement = getCommandEntry(id);
    const statusWrapper: HTMLElement = getChildWithClass(commandEntry, statusWrapperClass);
    const spinnerWrapper: HTMLElement = getChildWithClass(statusWrapper, spinnerWrapperClass)
    const undoButton: HTMLButtonElement = createUndoButton(id);
    const responseParagraph: HTMLElement = commandEntry.querySelector('.contentWrapper .responseWrapper .response')
    const isCommandDiscarded: boolean = responseParagraph.classList.contains('error-response');
    const isCommandUndone: boolean = commandEntry.classList.contains('undone');

    if (!statusWrapper || !spinnerWrapper) return;

    spinnerWrapper.remove();

    if (!isCommandDiscarded && !isCommandUndone) {
        statusWrapper.appendChild(undoButton);
    }
}



export function createExecutingFeedbackSpinner(): HTMLDivElement {
    const wrapper: HTMLDivElement = document.createElement('div');
    wrapper.classList.add(spinnerWrapperClass);
    const spinner: HTMLDivElement = document.createElement('div');
    spinner.classList.add("spinner");
    wrapper.appendChild(spinner);
    return wrapper;
}
