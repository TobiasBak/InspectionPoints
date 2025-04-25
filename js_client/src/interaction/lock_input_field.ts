import {CommandEnteredEvent, CommandFinishedEvent, EventList} from "./EventList";
import {inputField} from "./InputField";

document.addEventListener(EventList.CommandEntered, function (e: CommandEnteredEvent): void {
    lockInputField();
})

document.addEventListener(EventList.CommandFinished, function (e: CommandFinishedEvent): void {
    unlockInputField();
})

function lockInputField(): void {
    inputField.classList.add(lockedClass);
}

function unlockInputField(): void {
    inputField.classList.remove(lockedClass);
}

export const lockedClass = "locked"

