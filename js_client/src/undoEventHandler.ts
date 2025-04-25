import {EventList} from "./interaction/EventList";
import {getChildWithClass, getCommandEntry} from "./Toolbox/DomTools";

export const statusWrapperClass: string = "statusWrapper"



function markCommandElementsWithUndo(id: number): void {
    let running = true;
    while (running) {
        const commandEntry = getCommandEntry(id++)
        if (commandEntry) {
            const statusWrapper = getChildWithClass(commandEntry, statusWrapperClass);
            if(statusWrapper){
                let buttonToRemove = statusWrapper.querySelector('button');
                if(buttonToRemove){
                    buttonToRemove.remove();
                }
            }
            commandEntry.classList.add('undone');
        } else {
            running = false;
        }
    }
}

export function createUndoButton(commandId: number): HTMLButtonElement {
    const button: HTMLButtonElement = document.createElement('button');
    button.classList.add('undoButton');
    button.textContent = 'Undo up to here';
    button.addEventListener('click', function () {
        // document.dispatchEvent(new CustomEvent(EventList.UndoEvent, {detail: {id: commandId}}));
    })
    return button;
}


