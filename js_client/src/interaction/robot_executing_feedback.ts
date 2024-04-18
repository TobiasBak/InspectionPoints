import {EventList} from "./EventList";
import {getChildWithClass, getCommandEntry} from "../Toolbox/DomTools";

document.addEventListener(EventList.CommandFinished, function (e: CustomEvent): void {
    stopRobotExecutingFeedback(e.detail.id);
})

function stopRobotExecutingFeedback(id: number): void {
    const commandEntry: HTMLElement = getCommandEntry(id);
    const statusWrapper: HTMLElement = getChildWithClass(commandEntry, 'statusWrapper');
    const spinnerWrapper: HTMLElement = getChildWithClass(statusWrapper, spinnerWrapperClass)
    const undoButton: HTMLButtonElement = document.createElement('button');
    undoButton.onclick = function (): void {
        document.dispatchEvent(new CustomEvent(EventList.UndoEvent, {detail: {id: id}}));
    }
    undoButton.textContent = 'Undo up to here';

    spinnerWrapper.remove();
    statusWrapper.appendChild(undoButton);
}

const spinnerWrapperClass: string = "spinnerWrapper"

export function createExecutingFeedbackSpinner(): HTMLDivElement {
    const wrapper: HTMLDivElement = document.createElement('div');
    wrapper.classList.add(spinnerWrapperClass);
    const spinner: HTMLDivElement = document.createElement('div');
    spinner.classList.add("spinner");
    wrapper.appendChild(spinner);
    return wrapper;
}
