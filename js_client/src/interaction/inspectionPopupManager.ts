import { decorationIds } from "./inspectionPoints";

const customVariables = new Map<string, string[]>();
const checkedValues = new Map<string, string[]>();

export function openPopup(decorationId: string, x: number, y: number) {
    closePopup();

    const popup = document.createElement("div");
    popup.className = "inspectionpoint-popup-box";

    const savedVariables = customVariables.get(decorationId) || [];
    const savedCheckedValues = checkedValues.get(decorationId) || [
        "Joints",
        "Pose",
        "Speed",
        "Force",
        "Payload",
        "Digital_out",
    ];

    popup.innerHTML = `
        <div class="popup-header">
            <span>Track Variables</span>
            <button class="close-popup">&times;</button>
        </div>
        <div class="popup-body">
            <ul id="variableList">
                ${savedVariables.map((variable) => `<li>${variable}</li>`).join("")}
            </ul>
            <label for="customVariableInput">Track another variable:</label>
            <input type="text" id="customVariableInput" />
            <button id="saveVariableButton">Track</button>
            <div class="checkbox-group">
                <label><input type="checkbox" value="Joints" ${savedCheckedValues.includes("Joints") ? "checked" : ""}/> Joints</label>
                <label><input type="checkbox" value="Pose" ${savedCheckedValues.includes("Pose") ? "checked" : ""}/> Pose</label>
                <label><input type="checkbox" value="Speed" ${savedCheckedValues.includes("Speed") ? "checked" : ""}/> Speed</label>
                <label><input type="checkbox" value="Force" ${savedCheckedValues.includes("Force") ? "checked" : ""}/> Force</label>
                <label><input type="checkbox" value="Payload" ${savedCheckedValues.includes("Payload") ? "checked" : ""}/> Payload</label>
                <label><input type="checkbox" value="Digital_out" ${savedCheckedValues.includes("Digital_out") ? "checked" : ""}/> Digital_out</label>
            </div>
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
            if (!customVariables.has(decorationId)) {
                customVariables.set(decorationId, []);
            }
            customVariables.get(decorationId)?.push(input.value);

            const variableList = popup.querySelector("#variableList") as HTMLUListElement;
            const newVariableItem = document.createElement("li");
            newVariableItem.textContent = input.value;
            variableList.appendChild(newVariableItem);

            input.value = "";
        }
    });

    const checkboxes = popup.querySelectorAll(".checkbox-group input[type='checkbox']");
    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
            const checkedValuesArray = Array.from(checkboxes)
                .filter((cb) => (cb as HTMLInputElement).checked)
                .map((cb) => (cb as HTMLInputElement).value);

            checkedValues.set(decorationId, checkedValuesArray);
        });
    });

    const closeButton = popup.querySelector(".close-popup") as HTMLButtonElement;
    closeButton.addEventListener("click", closePopup);

    document.addEventListener("click", handleOutsideClick);
}

function closePopup() {
    const popup = document.querySelector(".inspectionpoint-popup-box");
    if (popup) {
        popup.remove();
        document.removeEventListener("click", handleOutsideClick);
    }
}

function handleOutsideClick(event: MouseEvent) {
    const popup = document.querySelector(".inspectionpoint-popup-box");
    if (popup && !popup.contains(event.target as Node)) {
        closePopup();
    }
}