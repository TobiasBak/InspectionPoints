import {EventList} from "./interaction/EventList";
import {getChildWithClass, getCommandEntry} from "./Toolbox/DomTools";
import {statusWrapperClass} from "./commandHistory";


document.addEventListener(EventList.UndoEvent, function (e: CustomEvent): void {
    markCommandElementsWithUndo(e.detail.id);
});


function markCommandElementsWithUndo(id: number): void {
    let running = true;
    while (running) {
        const element = getCommandEntry(id++)
        if (element) {
            const statusWrapper = getChildWithClass(element, statusWrapperClass);
            if(statusWrapper){
                let buttonToRemove = statusWrapper.querySelector('button');
                if(buttonToRemove){
                    buttonToRemove.remove();
                    statusWrapper.appendChild(generateUndoneFeedbackParagraph());
                }
            }
            element.classList.add('undone');
        } else {
            running = false;
        }
    }
}

function generateUndoneFeedbackParagraph(): HTMLElement {
    const undoneFeedback: HTMLParagraphElement = document.createElement('p');
    undoneFeedback.textContent = 'Command undone';
    undoneFeedback.classList.add('undone-feedback');
    return undoneFeedback;
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


