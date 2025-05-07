import {getColorMap} from "./ColorMap";
import {createVerticalLine, get2dLayout} from "./layoutFactory";
import {createDivForPlotlyChart} from "./chartDivFactory";
import * as Plotly from 'plotly.js';
import {getIndexFromClick, getTimestampFromClick} from "../toolbox";

const lineWeight = 3

export async function plotLineChart(chartName: string, chartId: string, lineNumbers: number[], dataArrays: number[][], customDatas: number[][], unit: string): Promise<Plotly.PlotlyHTMLElement> {
    const chartDiv = await createDivForPlotlyChart(chartId)

    const timestamps: Set<number> = new Set()
    dataArrays.forEach((inner) => {
        inner.forEach((value) => {
            timestamps.add(value)
        })
    })

    // Generate the layout. This is necessary for generating the frames
    const layout = get2dLayout(chartName, chartDiv.clientHeight, chartDiv.clientWidth - 50, false)

    layout.yaxis.ticksuffix = unit
    layout.annotations = [{
        x: 0.005,
        y: 10,
        xref: 'paper',
        yref: 'y',
        // yref: 'axis',
        text: "Target",
        showarrow: false,
        font: {
            family: 'Arial',
            size: 14,
            color: getColorMap().general.text_on_background
        }
    }]

    layout.legend.bgcolor = getColorMap().group_colors.A_background
    layout.legend.bordercolor = getColorMap().plot_colors.gridColor
    layout.legend.borderwidth = 1

    layout.xaxis.tickprefix = "Step "

    const ticktext = []
    const tickvals = []

    console.log(layout)

    // Enabling the things below would override the tick text and values
    // This would allow us to have different text in the hover box than shown on the x axis
    // layout.xaxis.ticktext = ticktext
    // layout.xaxis.tickvals = tickvals

    const frames: Partial<Plotly.Frame>[] = new Array(timestamps.size)

    let i = 0;
    for (const timestamp of timestamps) {
        const shapes = layout.shapes.slice()
        const line = createVerticalLine(timestamp, "stepCount")

        shapes.push(line)

        frames[i] = {
            name: timestamp.toString(),
            // data is an array, where each index corresponds to the index of a trace in the traces array
            // Since we only update one value, it will be the first trace in the traces array
            // We no longer update the data, but instead the shapes
            // This is because shapes allow us the flexibility to add vertical lines that span the paper
            // data: dataArray,
            layout: {
                shapes: shapes
            }
        }
        i++
    }


    const traces = generate_traces(lineNumbers, dataArrays, customDatas);

    const chart = await Plotly.react(chartDiv, traces, layout)

    const frameLookup: Record<string, Partial<Plotly.Frame>> = {}
    for (let i = 0; i < frames.length; i++) {
        frameLookup[frames[i].name] = frames[i]
    }


    chart.on('plotly_click', async function (data) {
        const index = getIndexFromClick(data)
        const timestamp = getTimestampFromClick(data)
        const customData = data.points[0].customdata
        console.log("plotly_click", data, index, timestamp, customData)
    })

    return chart
}

/**
 *
 * @param lineNumbers - The line numbers to plot. This will be the Y-axis of the individual traces
 * @param dataArrays - The data to plot. This must be sorted in the same order as the line numbers. dataArrays[i] has data for lineNumbers[i]
 * @param customDatas - Custom Data added to each point
 */
function generate_traces(lineNumbers: number[], dataArrays: number[][], customDatas: number[][]): Partial<Plotly.Data>[] {
    const traces: Partial<Plotly.Data>[] = []

    if (lineNumbers.length === 0 || lineNumbers.length > 6) {
        throw new Error("Invalid number of data names. It must be between 1 and 6. Both inclusive")
    }

    // Generate the traces for the data lines
    for (let i = 0; i < lineNumbers.length; i++) {
        const ys = dataArrays[i].map(() => lineNumbers[i])
        traces.push({
            x: dataArrays[i],
            y: ys,
            customdata: customDatas[i],
            type: 'scatter',
            name: lineNumbers[i].toString(),
            line: {
                color: getColorMap().legend_colors_array[i],
                width: lineWeight,
            },
        })
    }

    return traces
}


