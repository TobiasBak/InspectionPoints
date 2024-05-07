import {EventList} from "./EventList";
import {getChildWithTag, getCommandEntry} from "../Toolbox/DomTools";

document.addEventListener(EventList.UndoEvent, function (e: CustomEvent): void {
    const commandDisplay = document.getElementById('commandHistoryDisplay');
    commandDisplay.appendChild(generateCollapsableElement(e.detail.id));
    closeCollapsableElement(e.detail.id - 1);
    removeEmptyCollapsableElement();
})
document.addEventListener(EventList.CommandEntered, function (e: CustomEvent): void {
    closeCollapsableElement(e.detail.id - 1);
})


function generateCollapsableElement(id: number): HTMLElement {
    const collapsableWrapper: HTMLElement = document.createElement('div');
    const collapsableElement: HTMLElement = document.createElement('div');
    const collapsableParagraph: HTMLParagraphElement = document.createElement('p');
    collapsableParagraph.textContent = 'Press here to hide Undone commands';

    collapsableParagraph.addEventListener('click', function () {
        collapsableElement.classList.toggle('collapsed');
        if (collapsableElement.classList.contains('collapsed')) {
            collapsableParagraph.textContent = 'Press here to see Undone commands';
        } else {
            collapsableParagraph.textContent = 'Press here to hide Undone commands';
        }
    })

    collapsableWrapper.appendChild(collapsableParagraph);
    collapsableWrapper.appendChild(collapsableElement);

    collapsableWrapper.classList.add('collapsableWrapper');
    collapsableElement.classList.add('collapsable');

    const undoneCommands = getUndoneCommands(id);
    undoneCommands.forEach((element) => {
        collapsableElement.appendChild(element);
    })

    return collapsableWrapper;
}

function getUndoneCommands(id: number): HTMLElement[]{
    const listOfElements: Array<HTMLElement> = [];
    while (true)
    {
        const commandEntry = getCommandEntry(id++);
        if (!commandEntry) {
            break;
        }
        listOfElements.push(commandEntry);
    }
    return listOfElements;
}

export function openCollapsableElement(id: number): void {
    const commandEntry = getCommandEntry(id)
    const collapsableElement = commandEntry.parentElement
    const collapsableWrapper = collapsableElement.parentElement
    const collapsableParagraph = collapsableWrapper.querySelector('p');

    if (collapsableElement.classList.contains('collapsed')){
        collapsableParagraph.click();
    }
}

export function closeCollapsableElement(id: number): void {
    const commandEntry = getCommandEntry(id)
    if (!commandEntry) return;
    const collapsableElement = commandEntry.parentElement
    if (!collapsableElement.classList.contains('collapsable')) return;
    const collapsableWrapper = collapsableElement.parentElement
    const collapsableParagraph = collapsableWrapper.querySelector('p')

    if (!collapsableElement.classList.contains('collapsed')){
        collapsableParagraph.click();
    }
}

function removeEmptyCollapsableElement(): void {
    document.querySelectorAll('.collapsableWrapper').forEach((elementToRemove) => {
        const elementToCheck = elementToRemove.querySelector('.collapsable')
        if (elementToCheck.children.length < 1) {
            elementToRemove.remove();
        }
    })
}