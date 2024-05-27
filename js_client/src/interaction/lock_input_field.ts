import {EventList} from "./EventList";
import {inputField} from "./InputField";

document.addEventListener(EventList.CommandEntered, function (e: CustomEvent): void {
    lockInputField();
})

document.addEventListener(EventList.CommandFinished, function (e: CustomEvent): void {
    unlockInputField();
})

document.addEventListener(EventList.UndoEvent, function (e: CustomEvent): void {
    lockInputField();
})

function lockInputField(): void {
    inputField.classList.add(lockedClass);
}

function unlockInputField(): void {
    inputField.classList.remove(lockedClass);
}

export function inputFieldIsLocked(): boolean {
    return inputField.classList.contains(lockedClass);
}

export const lockedClass = "locked"

export function indicateToUserThatFieldIsLocked(): void {
    // Indicate to the user that the input field is locked
}
