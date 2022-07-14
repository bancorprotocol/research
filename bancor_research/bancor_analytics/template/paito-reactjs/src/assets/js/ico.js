(function($) {
    "use strict";

    // single bar chart
    var ctx = document.getElementById("singelBarChart");
    ctx.height = 100;
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ["Aug 2019", "Sep 2019", "Oct 2019", "Nov 2019", "Dec 2019", "Jan 2020", "Feb 2020"],
            datasets: [{
                label: "Demo",
                data: [40, 55, 75, 81, 56, 55, 40],
                borderColor: "transparent",
                borderWidth: "0",
                backgroundColor: "#080808a7"
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    },
                    gridLines: {
                        display: !1
                    }
                }],
                xAxes: [{
                    // Change here
                    barPercentage: 0.2,
                    gridLines: {
                        display: !1
                    }
                }]
            },
            legend: {
                display: false,


            },
        }
    });


    //doughut chart
    var ctx = document.getElementById("doughutChart1");
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
                "Bitcoin",
                "Ethereum",
                "Litecoin",
            ],
        },
        options: {
            responsive: true,
            legend: {
                display: false,


            },
            cutoutPercentage: 70,
        },
    });


})(jQuery);