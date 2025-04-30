import * as monaco from 'monaco-editor';
import { editor } from "../monacoExperiment";
import { createInspectionPointFormat, createDebugMessage } from '../userMessages/userMessageFactory';
import { InspectionPointFormat } from '../userMessages/userMessageDefinitions';
import { BeginDebugEvent } from './EventList';

const model = editor.getModel();
if (!model) {
    throw new Error("No model is attached to the editor.");
}

const decorationIds = new Map<string, number>();
const customVariables = new Map<string, string[]>();
const checkedValues = new Map<string, string[]>();

editor.onMouseDown((event) => {
    if (
        event.target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN ||
        event.target.type === monaco.editor.MouseTargetType.GUTTER_LINE_NUMBERS
    ) {
        const lineNumber = event.target.position?.lineNumber;
        if (!lineNumber) return;

        // Check if decoration is on this line
        let existingDecorationId: string | undefined;
        decorationIds.forEach((_, decorationId) => {
            const range = model.getDecorationRange(decorationId);
            if (range && range.startLineNumber === lineNumber) {
                existingDecorationId = decorationId;
            }
        });

        if (existingDecorationId) {
            if(event.event.rightButton) {
                console.log("event", event);
                event.event.preventDefault();
                event.event.stopPropagation();
                openPopup(existingDecorationId, event.event.posx, event.event.posy);
            } else {
                console.log("event", event.event);
            // Remove decoration
            model.deltaDecorations([existingDecorationId], []);
            decorationIds.delete(existingDecorationId);
            }
        } else {
            // Add decoration
            const [newId] = model.deltaDecorations([], [
                {
                    range: new monaco.Range(lineNumber, 1, lineNumber, 1),
                    options: {
                        isWholeLine: true,
                        glyphMarginClassName: 'red-circle-decoration',
                        stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
                    },
                },
            ]);

            decorationIds.set(newId, lineNumber);
        }
    }
});

// Function to collect decorated lines and create a BeginDebugEvent
function createDebugEvent(): BeginDebugEvent {
    const inspectionPointsMap = new Map<number, InspectionPointFormat>();
    let idCounter = 1;

    decorationIds.forEach((lineNumber, decorationId) => {
        const range = model.getDecorationRange(decorationId);
        if (range) {
            const currentLineNumber = range.startLineNumber;
            const lineContent = model.getLineContent(currentLineNumber);
            inspectionPointsMap.set(
                currentLineNumber,
                createInspectionPointFormat(idCounter++, currentLineNumber, lineContent)
            );
        }
    });

    const inspectionPoints = Array.from(inspectionPointsMap.values()).sort(
        (a, b) => a.lineNumber - b.lineNumber
    );

    const debugMessage = createDebugMessage(model.getLinesContent(), inspectionPoints).data;
    return new BeginDebugEvent(debugMessage);
}

const debugButton = document.getElementById("debugEditorButton");
//Ensure the button exists
if (debugButton) {
    debugButton.addEventListener("click", () => {
        const debugEvent = createDebugEvent();
        document.dispatchEvent(debugEvent);

        console.log("Debug event dispatched:", debugEvent);
    });
}

function openPopup(decorationId: string, x: number, y: number) {
    // If there's any other box open, close it
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
    ]; // Defaults all values to checked

    //Popup content
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

    // Popup near click position
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

    //Checkbox changes
    const checkboxes = popup.querySelectorAll(".radio-group input[type='checkbox']");
    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
            const checkedValuesArray = Array.from(checkboxes)
                .filter((cb) => (cb as HTMLInputElement).checked)
                .map((cb) => (cb as HTMLInputElement).value);

            checkedValues.set(decorationId, checkedValuesArray);
            console.log(`Checked values for ${decorationId}:`, checkedValuesArray);
        });
    });

    // Close popup
    const closeButton = popup.querySelector(".close-popup") as HTMLButtonElement;
    closeButton.addEventListener("click", closePopup);

    document.addEventListener("click", handleOutsideClick);
}

function closePopup() {
    const popup = document.querySelector(".popup-box");
    if (popup) {
        popup.remove();
        document.removeEventListener("click", handleOutsideClick);
    }
}

function handleOutsideClick(event: MouseEvent) {
    const popup = document.querySelector(".popup-box");
    if (popup && !popup.contains(event.target as Node)) {
        closePopup();
    }
}