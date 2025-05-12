import * as Plotly from "plotly.js";

export function getTimestampFromClick(data:  Plotly.PlotMouseEvent) {
    return data.points[data.points.length - 1].x;
}

export function getIndexFromClick(data: Plotly.PlotMouseEvent): number {
    const index = data.points[data.points.length - 1].customdata;
    if (typeof index !== 'number') {
        throw new Error(`Invalid customdata type: ${typeof index}`);
    }
    return index;
}