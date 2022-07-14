import React from 'react';
import { Doughnut } from 'react-chartjs-2';
export default function PieChartTwo() {
    const data = {
        labels: ['Litecoin', 'Ripple', 'Bitcoin'],
        datasets: [
            {
                data: [200, 150, 100],
                backgroundColor: ['#B0B0B0', '#345281', '#F7931A'],
                hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
            }
        ]
    };
    return (
        <div className="chart-2">
            <Doughnut 
             data={data} 
            options={{
                title: {
                    display: false,
                    text: 'ICO Distributions',
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
