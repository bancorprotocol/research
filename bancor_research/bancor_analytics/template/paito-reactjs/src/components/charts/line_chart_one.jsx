import React from 'react';
import { Line } from 'react-chartjs-2';
export default function LineChart() {
    const data = {
        labels: ['January', 'February', 'March',
            'April', 'May'],
        datasets: [
            {
                label: 'Rate',
                fill: false,
                lineTension: 0.3,
                backgroundColor: 'rgba(75,192,192,.5)',
                borderColor: 'rgba(30, 146, 111,.9)',
                borderWidth: 2,
                data: [65, 59, 80, 81, 56]
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
