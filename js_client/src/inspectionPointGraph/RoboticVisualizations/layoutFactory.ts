import {getColorMap} from "./ColorMap";
import * as Plotly from 'plotly.js';

export function createVerticalLine(x: number, lineName: string, thickness: number = 2): Partial<Plotly.Shape> {
    return {
        type: "line",
        xref: "x",
        yref: "paper",
        x0: x,
        y0: 0,
        x1: x,
        y1: 1,

        layer: "above",


        line: {
            width: thickness,
            color: getColorMap().legend_colors.connecting_line
        },
        label: {
            text: lineName,
            font: {size: 10, color: getColorMap().general.text_on_background},
            textposition: 'top center',
        },
    }
}

/**
 *
 * @param title {string}
 * @param height {number}
 * @param width {number}
 * @param forLinePlot {boolean} - If true, the layout will be for a line plot, otherwise it will be for other types of 2d plots
 * @param showLegend {boolean} - When true the legend will be displayed, when false the legend is hidden
 * @returns Object
 */
export function get2dLayout(title: string, height: number, width: number, forLinePlot: boolean = true, showLegend: boolean = true): Partial<Plotly.Layout> {
    const {plotColor, paperColor, gridColor} = getColorMap().plot_colors

    return {
        title: {
            text: title
        },
        hovermode: forLinePlot ? "x unified" : "closest",
        autosize: false,
        width: width,
        height: height,
        margin: {
            l: 0,
            r: 0,
            b: 25,
            t: 30,
            pad: 4
        },
        xaxis: {
            automargin: true,
            spikethickness: -2, // Enabling this removes the color surrounding the spike line
            showspikes: forLinePlot,
            gridcolor: gridColor,
            gridwidth: 1,
            showline: forLinePlot,
            showgrid: showLegend,
        },
        yaxis: {
            automargin: true,
            gridcolor: gridColor,
            gridwidth: 1,
            showline: forLinePlot,
            autorange: "reversed",
            // dtick: 1,
            // tick0: 1,
            // showgrid: showLegend,
        },
        plot_bgcolor: plotColor,
        paper_bgcolor: paperColor,
        dragmode: "zoom",
        //https://plotly.com/javascript/shapes/
        shapes: [],
        showlegend: showLegend,
        legend: {
            //https://plotly.com/javascript/reference/layout/#layout-legend-xanchor
            x: 1, // this is the paper coordinate of the plot
            xanchor: 'right', // right means that the position is calculated from the right side of the legend
            yanchor: 'top',
            y: 1,
            font: {
                color: getColorMap().general.text_on_background
            },
            // orientation: "h",
        }
    }
}