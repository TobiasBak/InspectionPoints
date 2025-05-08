import * as Plotly from 'plotly.js';
import {Datum} from "plotly.js";
import {getIndexFromClick, getTimestampFromClick} from "./toolbox";
import {plotLineChart, TraceData} from "./RoboticVisualizations/LinePlotFactory";
import {displayMessageData, getStoredMessages} from "../responseMessages/displayReportStateMessage";
import {getLineNumberFromInspectionPointId} from "../interaction/inspectionPoints";


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

    for (let i = 0; i < storage.length; i++) {
        const index = i
        const message = storage[index]
        const x = index + 1
        const y = message.id


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
            xs: dataCollection.map((dotInfo) => dotInfo.x),
            ys: getLineNumberFromInspectionPointId(yValue),
            customDatas: dataCollection.map((dotInfo) => dotInfo.customdata),
        })
    }

    const chart = await plotLineChart("Inspection points logged", "newChart", traceData, "lineNumber");

    chart.removeAllListeners('plotly_click')

    chart.on('plotly_click', async function (data) {
        const index = getIndexFromClick(data)
        const timestamp = getTimestampFromClick(data)
        const customData = data.points[0].customdata
        console.log("plotly_click", data, index, timestamp, customData)

        const message = storage[index]
        displayMessageData(message)
    })

    return chart
}
