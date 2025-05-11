import * as Plotly from 'plotly.js';
import {Datum} from "plotly.js";
import {getIndexFromClick, getTimestampFromClick} from "./toolbox";
import {plotLineChart, TraceData} from "./RoboticVisualizations/LinePlotFactory";
import {displayMessageData, getCurrentId, getStoredMessages} from "../responseMessages/displayReportStateMessage";
import {getLineNumberFromInspectionPointId} from "../interaction/debugEventHandler";
import {clone} from "../Toolbox/DomTools";
import {registerForSpinnerStateChange} from "../responseMessages/RtdeStateMessageHandler";

let activeChart: Plotly.PlotlyHTMLElement | null = null
let activeButton: HTMLElement | null = null

export async function refreshGraph(): Promise<Plotly.PlotlyHTMLElement> {
    const storage = getStoredMessages()

    type DotInfo = {
        x: number,
        customdata: number,
    }

    /**
     * Maps y-axis values to an array of x-axis values
     */
    const dataCollections: Map<number, DotInfo[]> = new Map()

    let lowest_x = Number.MAX_VALUE

    for (let i = 0; i < storage.length; i++) {
        const index = i
        const message = storage[index]
        const x = message.timestamp
        const y = message.id

        lowest_x = x < lowest_x ? x : lowest_x

        if (!dataCollections.has(y)){
            dataCollections.set(y, [])
        }
        const dataCollection = dataCollections.get(y)
        dataCollection.push({
            x: x,
            customdata: index,
        })
    }

    const traceData: TraceData = []

    for (const yValue of dataCollections.keys()) {
        const dataCollection = dataCollections.get(yValue)
        if (!dataCollection) {
            continue
        }
        traceData.push({
            xs: dataCollection.map((dotInfo) => (dotInfo.x - lowest_x) / 1000),
            ys: getLineNumberFromInspectionPointId(yValue),
            customDatas: dataCollection.map((dotInfo) => dotInfo.customdata),
        })
    }

    const newTraceData = traceData.sort((a, b) => {
        const anumber = typeof a.ys === "number" ? a.ys : a.ys[0]
        const bnumber = typeof b.ys === "number" ? b.ys : b.ys[0]

        return anumber - bnumber
    })

    const chart = await plotLineChart(`Run ${getCurrentId()} - Inspection points logged:`, `newchart-${getCurrentId()}`, newTraceData, "line");
    if (activeChart && activeChart.id !== chart.id) {
        activeChart.classList.add("hidden")
        activeButton?.classList.remove("active")
    }
    activeChart = chart


    chart.removeAllListeners('plotly_click')

    chart.on('plotly_click', async function (data) {
        const index = getIndexFromClick(data)
        const timestamp = getTimestampFromClick(data)
        const customData = data.points[0].customdata
        console.log("plotly_click", data, index, timestamp, customData)

        const message = storage[index]
        displayMessageData(message)
    })

    let showGraphButton = document.getElementById(`graph-button-${getCurrentId()}`)
    if (!showGraphButton) {
        const templateButton: HTMLElement = document.getElementById("graph-button-template")
        showGraphButton = clone(templateButton)
        showGraphButton.id = `graph-button-${getCurrentId()}`
        showGraphButton.classList.remove("hidden")
        const container = document.getElementById("graph-button-container")
        showGraphButton.textContent = `${getCurrentId()}`
        container.appendChild(showGraphButton)
    }

    function showThisGraph() {
        activeChart?.classList.add("hidden")
        chart.classList.remove("hidden")
        activeChart = chart
        activeButton?.classList.remove("active")
        showGraphButton?.classList.add("active")
        activeButton = showGraphButton
    }
    activeButton = showGraphButton

    showGraphButton.removeEventListener("click", showThisGraph)
    showGraphButton.addEventListener("click", showThisGraph)

    if (showGraphButton instanceof HTMLButtonElement) {
        registerForSpinnerStateChange((enabled: boolean) => {
            enableButton(showGraphButton, enabled)
        })
    }

    return chart
}

function enableButton(button: HTMLButtonElement, enabled: boolean) {
    button.disabled = enabled
}
