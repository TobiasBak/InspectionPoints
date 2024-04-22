import {EventList} from "./interaction/EventList";
import {getCommandEntry} from "./Toolbox/DomTools";


document.addEventListener(EventList.UndoEvent, function (e: CustomEvent): void {
    markCommandElementsWithUndo(e.detail.id);
});


function markCommandElementsWithUndo(id: number): void {
    let running = true;
    while (running) {
        const element = getCommandEntry(id++)
        if (element) {
            element.classList.add('undone');
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
        document.dispatchEvent(new CustomEvent(EventList.UndoEvent, {detail: {id: commandId}}));
    })
    return button;
}


