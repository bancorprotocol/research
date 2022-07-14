(function($) {
    "use strict";

    //Team chart
    var ctx = document.getElementById("team-chart");
    ctx.height = 120;
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ["2010", "2011", "2012", "2013", "2014", "2015", "2016"],
            type: 'line',
            datasets: [{
                    data: [0, 15, 27, 12, 85, 10, 50],  
                    label: "Saiful",
                    backgroundColor: 'rgba(30,146,120,.5)',
                    borderColor: 'rgba(30,146,120,.5)',
                    borderWidth: 0.5,
                    pointStyle: 'circle',
                    pointRadius: 5,
                    pointBorderColor: 'transparent',
                    pointBackgroundColor: '#1D9378',
                },
                {
                    label: "Saikot",
                    data: [0, 25, 15, 30, 20, 55, 50],
                    backgroundColor: 'transparent',
                    borderColor: 'rgba(0,0,0,.75)',
                    borderWidth: 2,
                    // pointStyle: 'circle',
                    pointRadius: 5,
                    pointBorderColor: 'transparent',
                    pointBackgroundColor: 'transparent',
                }
            ]
        },
        options: {
            responsive: true,
            tooltips: {
                mode: 'index',
                titleFontSize: 12,
                titleFontColor: '#000',
                bodyFontColor: '#000',
                backgroundColor: '#fff',
                cornerRadius: 3,
                intersect: false,
            },
            legend: {
                position: 'top',
                display: false


            },
            scales: {
                xAxes: [{
                    display: true,
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    scaleLabel: {
                        display: false,
                        labelString: 'Month'
                    }
                }],
                yAxes: [{
                    display: true,
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Value'
                    }
                }]
            },
            title: {
                display: false,
            }
        }
    });

    //doughut chart
    var ctx = document.getElementById("doughutChart");
    ctx.height = 100;
    var myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [45, 25, 20],
                backgroundColor: [
                    "#F6931A",
                    "#1276A8",
                    "#B0B0B0",
                ],
                hoverBackgroundColor: [
                    "rgba(55,160,0,0.9)",
                    "rgba(55,160,0,0.7)",
                    "rgba(55,160,0,0.5)",
                ],

            }],
            labels: [
                "green",
                "green",
                "green",
            ],
        },
        options: {
            responsive: true,
            legend: {
                position: 'right',


            },
        },
    });

})(jQuery);