import React from 'react'
import { Bar } from 'react-chartjs-2';
export default function BarChartOne() {
    const chartData = {
        labels: ['January', 'February', 'March',
            'April', 'May', "June", "July", "August"],
        datasets: [
            {
                label: 'ICO',
                backgroundColor: 'rgba(52,58,64,.9)',
                borderColor: 'rgba(0,0,0,1)',
                borderWidth: 0,
                data: [65, 59, 80, 81, 56.,90,75,10]
            }
        ]
    }
    return (
        <div>
            <Bar
                data={chartData}
                options={{
                    title: {
                        display: false,
                        text: 'Average Rainfall per month',
                        fontSize: 20
                    },
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                }}
            />
        </div>
    )
}
