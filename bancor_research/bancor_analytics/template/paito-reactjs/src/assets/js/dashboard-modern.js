(function($) {
    "use strict";

    
    //Team chart
    var ctx = document.getElementById("team-chart-two");
    ctx.height = 120;
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ["2014", "2015", "2016", "2017", "2018", "2019", "2020"],
            type: 'line',
            datasets: [{
                    data: [0, 15, 27, 12, 85, 10, 50],
                    label: "demo1",
                    backgroundColor: 'transparent',
                    borderColor: '#1277A8',
                    borderWidth: 2,
                    pointStyle: 'circle',
                    pointRadius: 5,
                    pointBorderColor: 'transparent',
                    pointBackgroundColor: 'rgba(0,0,0,1)',
                },
                {
                    label: "demo2",
                    data: [0, 25, 15, 30, 20, 55, 50],
                    backgroundColor: 'transparent',
                    borderColor: '#f7931a',
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
                borderWidt: 100,

            }],
            labels: [
                "Bitcoin",
                "Ethereum",
                "Litecoin",
            ],
        },
        options: {
            responsive: true,
            legend: {
                position: 'right',


            },
            cutoutPercentage: 70,
        },
    });

})(jQuery);