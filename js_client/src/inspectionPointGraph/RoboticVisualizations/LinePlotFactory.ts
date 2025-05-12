import {getColorMap} from "./ColorMap";
import {get2dLayout} from "./layoutFactory";
import {createDivForPlotlyChart} from "./chartDivFactory";
import * as Plotly from 'plotly.js';
import {Datum} from 'plotly.js';

const lineWeight = 3

export type TraceData = {
    xs: number[]
    ys: number[] | number
    customDatas: number[]
}[]

export async function plotLineChart(chartName: string, chartId: string, traceData: TraceData, yUnit: string): Promise<Plotly.PlotlyHTMLElement> {
    const chartDiv = await createDivForPlotlyChart(chartId)

    // Generate the layout. This is necessary for generating the frames
    console.log(`Generating layout for ${chartName} with height: ${chartDiv.clientHeight} and width: ${chartDiv.clientWidth}`, chartDiv.clientHeight, chartDiv)
    const layout = get2dLayout(chartName, chartDiv.clientHeight, chartDiv.clientWidth - 50, false, false)

    layout.yaxis.tickprefix = `${yUnit} `

    layout.legend.bgcolor = getColorMap().group_colors.A_background
    layout.legend.bordercolor = getColorMap().plot_colors.gridColor
    layout.legend.borderwidth = 1

    layout.xaxis.tickprefix = `Time `
    layout.xaxis.ticksuffix = ` (s)`

    const traces = generate_traces(traceData);

    return await Plotly.react(chartDiv, traces, layout)
}


function generate_traces(traceData: TraceData): Partial<Plotly.Data>[] {
    const traces: Partial<Plotly.Data>[] = []

    // if (traceData.length === 0 || traceData.length > 6) {
    //     throw new Error("Invalid number of data names. It must be between 1 and 6. Both inclusive")
    // }

    // Generate the traces for the data lines
    for (let i = 0; i < traceData.length; i++) {
        traces.push(generateTrace(traceData[i].xs, traceData[i].ys, traceData[i].customDatas, `Line ${traceData[i].ys}`, i % 6))
    }

    return traces
}

function generateTrace(x: Datum[], y: Datum | Datum[], customData: Datum[], name: string, color: number): Partial<Plotly.Data> {
    let newY: Datum[] = []
    if (!Array.isArray(y)) {
        newY = x.map(() => y)
    } else {
        newY = y
    }

    return {
        x: x,
        y: newY,
        customdata: customData,
        type: 'scatter',
        mode: 'markers',
        name: name,
        line: {
            color: getColorMap().legend_colors_array[color],
            width: lineWeight,
        },
        marker: {
            size: 15
        }
    }
}


