import * as Plotly from 'plotly.js';
import {Datum} from "plotly.js";
import {getIndexFromClick, getTimestampFromClick} from "./toolbox";
import {plotLineChart} from "./RoboticVisualizations/LinePlotFactory";

const data: Partial<Plotly.ScatterData>[] = [
    {
        x: [],
        y: [],
        mode: 'markers',
        type: 'scatter',
        customdata: []
    }
];

export function addDataPoint(x: number, y: number, index: number){
    const newX: Datum[] = []
    const newY: Datum[] = []

    data[0].x.forEach((element) => {
        newX.push(<Datum>element)
    })

    data[0].y.forEach((element) => {
        newY.push(<Datum>element)
    })

    data[0].customdata[data[0].customdata.length] = index

    newX.push(x)
    newY.push(y)

    const largestX = newX.reduce((previousValue, currentValue, currentIndex, array) => {
        return currentValue > previousValue ? currentValue : previousValue;
    })

    const largestY = newY.reduce((previousValue, currentValue, currentIndex, array) => {
        return currentValue > previousValue ? currentValue : previousValue;
    })

    data[0].x = newX
    data[0].y = newY

    if (typeof largestX === "number") {
        layout.xaxis.range[1] = largestX + 0.25
    }else {
        console.warn("wrong type for largestX", largestX)
    }

    if (typeof largestY === "number") {
        layout.yaxis.range[1] = largestY + 0.25
    }else {
        console.warn("wrong type for largestY", largestY)
    }

    console.log("addDataPoint", data[0], x,y);

    Plotly.react('test', data, layout)
}

const layout: Partial<Plotly.Layout> = {
    xaxis: {
        range: [0.75, 5.25]
    },
    yaxis: {
        range: [0, 5]
    },
    title: {text: 'Data Labels Hover'}
};


const chart = await (async () => {
    return await plotLineChart("Hello-world", "newChart", [1,2,5], [
        [1,2,3,4,5],
        [2,3,4,5,6],
        [3,4,5,6,7],
    ],[
        [1,2,3,4,5],
        [2,3,4,5,6],
        [3,4,5,6,7],
    ], "myunit");
    // return Plotly.react('test', data, layout);
})();



chart.on(
    "plotly_click",
    async function (data) {
        console.log(data, getTimestampFromClick(data), getIndexFromClick(data));
    }
)