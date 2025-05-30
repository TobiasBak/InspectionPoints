export async function createDivForPlotlyChart(chartId: string): Promise<HTMLElement> {
    // check whether the div already exists
    if (document.getElementById(chartId) !== null) {
        // Check if it has the correct shape?
        return document.getElementById(chartId)
    }

    // create div since it does not exist yet
    const div = _createDiv(chartId)

    // Create the heading inside that gets the loading text
    const heading = document.createElement("h1")

    // Add the heading to the div as a child
    div.appendChild(heading)

    //Add the div to the container that has the visualizations
    const visualizationContainer = document.getElementById("visualization-container")
    console.log(visualizationContainer)
    visualizationContainer.prepend(div)

    return div
}


function _createDiv(id: string): HTMLDivElement {
    const div = document.createElement("div")

    // Add the classes to the div for placeholder text and formatting
    div.id = id
    div.classList.add("vis-placeholder", "draggable", "slate")
    div.draggable = false

    return div
}


export async function createDivsForPlotlyCharts(chartIds: string[]) : Promise<Record<string, HTMLElement>> {

    const divs: Record<string, HTMLElement> = {}
    for (let chartId of chartIds) {
        divs[chartId] = await createDivForPlotlyChart(chartId)
    }

    return divs
}


export async function createDivForTable(chartId: string, tableId: string, tableHeaders: string[]) {
    // check whether the div already exists
    let div = document.getElementById(chartId);
    if (div !== null) {
        // Check if it has the correct shape?
        if (div.childNodes.length === 1 && div.childNodes[0].nodeName === "TABLE") {
            return div
        }
    } else {
        div = _createDiv(chartId)

        //Add the div to the container that has the visualizations
        document.getElementById("visualization-container").appendChild(div)
    }

    const table = document.createElement("table")
    table.id = tableId

    const tableBody = document.createElement("tbody")
    const headerRow = document.createElement("tr")

    table.appendChild(tableBody)
    tableBody.appendChild(headerRow)

    for (let header of tableHeaders){
        const tableHead = document.createElement("th")
        tableHead.innerText = header
        headerRow.appendChild(tableHead)
    }

    div.appendChild(table)

    return div
}