export function getChildWithTag(node: HTMLElement, tagName: string): HTMLElement | null {
    const children = node.children;
    for (let i = 0; i < children.length; i++) {
        if (children[i].tagName === tagName) {
            return children[i] as HTMLElement;
        }
    }
    return null;
}

export function getChildWithClass(node: HTMLElement, className: string): HTMLElement | null {
    const children = node.children;
    for (let i = 0; i < children.length; i++) {
        if (children[i].classList.contains(className)) {
            return children[i] as HTMLElement;
        }
    }
    return null;
}

export function getCommandEntry(id: number): HTMLElement | null {
    return document.getElementById(`command-${id}`);
}


export function clone<T extends Node>(node: T){
    return <T>node.cloneNode(true);
}