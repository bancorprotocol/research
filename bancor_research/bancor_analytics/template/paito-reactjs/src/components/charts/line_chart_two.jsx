import React from 'react';
import { Line } from 'react-chartjs-2';
export default function LineChartTwo() {
    const data = {
        labels: ['June', 'July', 'August',
            'September', 'October'],
        datasets: [
            {
                label: 'Sales',
                fill: false,
                lineTension: 0.3,
                backgroundColor: 'rgba(75,192,192,.6)',
                borderColor: 'rgba(0,0,0,.5)',
                borderWidth: 2,
                data: [25, 49, 30, 85, 10]
            }
        ]
    }
    return (
        <div>
            <Line
                data={data}
                options={{
                    title: {
                        display: true,
                        text: '',
                        fontSize: 20
                    },
                    legend: {
                        display: true,
                        position: 'right'
                    }
                }}
            />
        </div>
    )
}
