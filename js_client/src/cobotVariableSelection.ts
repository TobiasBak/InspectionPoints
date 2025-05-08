import { InspectionVariable } from "./userMessages/userMessageDefinitions";

const GLOBAL_DEBUG_VARIABLES: InspectionVariable[] = [
    { name: "joints", readCommand: "get_actual_joint_positions()" },
    { name: "pose", readCommand: "get_actual_tcp_pose()" },
    { name: "speed", readCommand: "get_actual_joint_speeds()" },
    { name: "force", readCommand: "get_tcp_force()" },
    { name: "payload", readCommand: "get_target_payload()" },
    { name: "digital_out0", readCommand: "get_digital_out(0)" },
    { name: "digital_out1", readCommand: "get_digital_out(1)" },
    { name: "digital_out2", readCommand: "get_digital_out(2)" },
    { name: "digital_out3", readCommand: "get_digital_out(3)" },
    { name: "digital_out4", readCommand: "get_digital_out(4)" },
    { name: "digital_out5", readCommand: "get_digital_out(5)" },
    { name: "digital_out6", readCommand: "get_digital_out(6)" },
    { name: "digital_out7", readCommand: "get_digital_out(7)" },
];

export let selectedGlobalVariables = [...GLOBAL_DEBUG_VARIABLES];

export function populateSelectGlobalVariableMenu(): void {
    const dropdownMenu = document.getElementById("stateVariableSelection");
    if (!dropdownMenu) return;

    dropdownMenu.innerHTML = "";

    GLOBAL_DEBUG_VARIABLES.forEach((variable) => {
        const listItem = document.createElement("li");
        const checkboxDiv = document.createElement("div");
        checkboxDiv.classList.add("form-check", "dropdown-item");

        const checkbox = document.createElement("input");
        checkbox.classList.add("form-check-input");
        checkbox.type = "checkbox";
        checkbox.id = `checkbox-${variable.name}`;
        checkbox.checked = true;
        checkbox.value = variable.readCommand;

        const label = document.createElement("label");
        label.classList.add("form-check-label");
        label.htmlFor = `checkbox-${variable.name}`;
        label.textContent = `${variable.name}`;

        checkbox.addEventListener("change", () => {
            if (checkbox.checked) {
                selectedGlobalVariables.push(variable);
            } else {
                selectedGlobalVariables = selectedGlobalVariables.filter((v) => v.name !== variable.name);
            }
        });

        checkboxDiv.appendChild(checkbox);
        checkboxDiv.appendChild(label);
        listItem.appendChild(checkboxDiv);
        dropdownMenu.appendChild(listItem);
    });
}

// Populate the dropdown menu when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", populateSelectGlobalVariableMenu);