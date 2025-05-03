export const inspectionVariables = new Map<string, string[]>();

export function openPopup(decorationId: string, x: number, y: number) {
    closePopup();

    const popup = document.createElement("div");
    popup.className = "inspectionpoint-popup-box";

    const savedVariables = inspectionVariables.get(decorationId) || [];

    popup.innerHTML = `
        <div class="popup-header">
            <span>Track Variables</span>
            <button class="close-popup">&times;</button>
        </div>
        <div class="popup-body">
            <ul id="variableList">
            ${savedVariables
                .map(
                    (variable, index) => `
                    <li>
                        ${variable}
                        <button class="delete-variable" data-index="${index}" title="Delete">Delete</button>
                    </li>`
                )
                .join("")}
            </ul>
            <label for="customVariableInput">Track another variable:</label>
            <input type="text" id="customVariableInput" />
            <button id="saveVariableButton">Track</button>
        </div>
    `;

    document.body.appendChild(popup);

    popup.style.position = "absolute";
    popup.style.left = `${x}px`;
    popup.style.top = `${y}px`;

    const saveButton = popup.querySelector("#saveVariableButton") as HTMLButtonElement;
    saveButton.addEventListener("click", () => {
        const input = popup.querySelector("#customVariableInput") as HTMLInputElement;
        if (input && input.value) {
            if (!inspectionVariables.has(decorationId)) {
                inspectionVariables.set(decorationId, []);
            }
            const variables = inspectionVariables.get(decorationId)!;
            variables.push(input.value);

            const variableList = popup.querySelector("#variableList") as HTMLUListElement;
            const newVariableItem = document.createElement("li");
            newVariableItem.innerHTML = 
            `
                ${input.value}
                <button class="delete-variable" data-index="${variables.length - 1}" title="Delete">Delete</button>
            `;
            variableList.appendChild(newVariableItem);

            deleteTrackedVariable(newVariableItem, decorationId);

            input.value = "";
        }
    });

    const closeButton = popup.querySelector(".close-popup") as HTMLButtonElement;
    closeButton.addEventListener("click", closePopup);

    document.addEventListener("click", handleOutsideClick);

    const deleteButtons = popup.querySelectorAll(".delete-variable");
    deleteButtons.forEach((button) => {
        deleteTrackedVariable(button.parentElement as HTMLElement, decorationId);
    });
}

function closePopup() {
    const popup = document.querySelector(".inspectionpoint-popup-box");
    if (popup) {
        popup.remove();
        document.removeEventListener("click", handleOutsideClick);
    }
}

function deleteTrackedVariable(variableItem: HTMLElement, decorationId: string) {
    const deleteButton = variableItem.querySelector(".delete-variable") as HTMLButtonElement;
    deleteButton.addEventListener("click", (event) => {
        event.stopPropagation();
        const index = parseInt(deleteButton.dataset.index, 10);
        const trackedVariables = inspectionVariables.get(decorationId);
        if (trackedVariables) {
            trackedVariables.splice(index, 1);
            variableItem.remove();
        }
    });
}

function handleOutsideClick(event: MouseEvent) {
    const popup = document.querySelector(".inspectionpoint-popup-box");
    if (popup && !popup.contains(event.target as Node)) {
        closePopup();
    }
}