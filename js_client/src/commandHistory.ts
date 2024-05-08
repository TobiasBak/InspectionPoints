import {EventList} from "./interaction/EventList";
import {highlightCommandIntoElement} from "./SyntaxHighlighting/hast-starry-night";
import {getCommandEntry} from "./Toolbox/DomTools";
import {closeCollapsableElement, openCollapsableElement} from "./interaction/collapseUndoneCommands";

document.addEventListener(EventList.CommandEntered, function (e: CustomEvent): void {
    createCommandContainer(e.detail.text, e.detail.id);
});

export const commandHistoryDisplay: HTMLElement = document.getElementById("commandHistoryDisplay");
export const statusWrapperClass = "statusWrapper";

function createCommandContainer(text: string, id: number): void {
    const wrapperElement: HTMLDivElement = document.createElement('div');
    wrapperElement.id = `command-${id}`;
    wrapperElement.classList.add('field', 'flex');

    const idWrapper: HTMLDivElement = document.createElement('div');
    idWrapper.classList.add('idWrapper', 'column10', 'center');

    const contentWrapper: HTMLDivElement = document.createElement('div');
    contentWrapper.classList.add('contentWrapper', 'column70');

    const statusWrapper: HTMLDivElement = document.createElement('div');
    statusWrapper.classList.add(statusWrapperClass, 'column20', 'center');

    const commandWrapper: HTMLDivElement = document.createElement('div');
    commandWrapper.classList.add('commandWrapper');

    const responseWrapper: HTMLDivElement = document.createElement('div');
    responseWrapper.classList.add('responseWrapper');

    const idText: HTMLParagraphElement = document.createElement('p');

    idText.textContent = id.toString();

    idWrapper.appendChild(idText);

    contentWrapper.appendChild(commandWrapper);
    contentWrapper.appendChild(responseWrapper);

    wrapperElement.appendChild(idWrapper);
    wrapperElement.appendChild(contentWrapper);
    wrapperElement.appendChild(statusWrapper);

    highlightCommandIntoElement(text, commandWrapper);

    commandHistoryDisplay.appendChild(wrapperElement).scrollIntoView({behavior: "smooth"})
}

export function highlightSelectedCommandItem(id: number): void {
    const selectedElement: HTMLElement = getCommandEntry(id);
    if (selectedElement) {
        selectedElement.classList.add('command-highlighted');
        openCollapsableElement(id);
        selectedElement.scrollIntoView({behavior: "smooth", block: "nearest", inline: "nearest"});
    }
}

export function clearHighlightedCommandItems():void  {
    const highlightedElement: HTMLElement = document.querySelector('.command-highlighted');
    if (highlightedElement) {
        highlightedElement.classList.remove('command-highlighted');
    }
}