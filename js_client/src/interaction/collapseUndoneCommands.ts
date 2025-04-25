import {CommandEnteredEvent, EventList} from "./EventList";
import {getChildWithTag, getCommandEntry} from "../Toolbox/DomTools";


document.addEventListener(EventList.CommandEntered, function (e: CommandEnteredEvent): void {
    closeCollapsibleElement(e.detail.id - 1);
})


function generateCollapsibleElement(id: number): HTMLElement {
    const collapsibleWrapper: HTMLElement = document.createElement('div');
    const collapsibleElement: HTMLElement = document.createElement('div');
    const collapsibleParagraph: HTMLParagraphElement = document.createElement('p');
    collapsibleParagraph.textContent = 'Press here to hide Undone commands';

    collapsibleParagraph.addEventListener('click', function () {
        collapsibleElement.classList.toggle('collapsed');
        if (collapsibleElement.classList.contains('collapsed')) {
            collapsibleParagraph.textContent = 'Press here to see Undone commands';
        } else {
            collapsibleParagraph.textContent = 'Press here to hide Undone commands';
        }
    })

    collapsibleWrapper.appendChild(collapsibleParagraph);
    collapsibleWrapper.appendChild(collapsibleElement);

    collapsibleWrapper.classList.add('collapsibleWrapper');
    collapsibleElement.classList.add('collapsible');

    const undoneCommands: HTMLElement[] = getUndoneCommands(id);
    undoneCommands.forEach((element: HTMLElement): void => {
        collapsibleElement.appendChild(element);
    })

    return collapsibleWrapper;
}

function getUndoneCommands(id: number): HTMLElement[]{
    const listOfElements: Array<HTMLElement> = [];
    while (true)
    {
        const commandEntry: HTMLElement = getCommandEntry(id++);
        if (!commandEntry) {
            break;
        }
        listOfElements.push(commandEntry);
    }
    return listOfElements;
}

export function openCollapsibleElement(id: number): void {
    const commandEntry: HTMLElement = getCommandEntry(id)
    const collapsibleElement: HTMLElement = commandEntry.parentElement
    const collapsibleWrapper: HTMLElement = collapsibleElement.parentElement
    const collapsibleParagraph: HTMLParagraphElement = collapsibleWrapper.querySelector('p');

    if (collapsibleElement.classList.contains('collapsed')){
        collapsibleParagraph.click();
    }
}

export function closeCollapsibleElement(id: number): void {
    const commandEntry: HTMLElement = getCommandEntry(id)
    if (!commandEntry) return;
    const collapsibleElement: HTMLElement = commandEntry.parentElement
    if (!collapsibleElement.classList.contains('collapsible')) return;
    const collapsibleWrapper: HTMLElement = collapsibleElement.parentElement
    const collapsibleParagraph: HTMLParagraphElement = collapsibleWrapper.querySelector('p')

    if (!collapsibleElement.classList.contains('collapsed')){
        collapsibleParagraph.click();
    }
}

function removeEmptyCollapsibleElement(): void {
    document.querySelectorAll('.collapsibleWrapper').forEach((elementToRemove: Element): void => {
        const elementToCheck: Element = elementToRemove.querySelector('.collapsible')
        if (elementToCheck.children.length < 1) {
            elementToRemove.remove();
        }
    })
}