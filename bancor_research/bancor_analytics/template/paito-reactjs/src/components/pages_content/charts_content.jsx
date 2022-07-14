import React from 'react';
import BarChartTwo from "../charts/bar_chart_two";
import BarChartOne from "../charts/bar_chart_one";
import PieChartTwo from "../charts/pie_chart_two";
import PieChartOne from "../charts/pie_chart_one";
import LineChartOne from "../charts/line_chart_one";
import LineChartTwo from "../charts/line_chart_two";

export default function ChartsContent() {
    return (
        <div className="content-body">
            <div className="container-fluid">
                <div className="row">
                    <div className="col-lg-12">
                        <h2 className="page-title">Charts</h2>
                    </div>
                </div>
                <div className="row m-b-30">
                    <div className="col-lg-12">
                        <div className="card single-chart">
                            <div className="card-header">
                                <h4>Trading</h4>
                            </div>
                            <div className="card-body">
                                <BarChartTwo/>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="row m-b-30">
                    <div className="col-lg-8">
                        <div className="card single-chart">
                            <div className="card-header">
                                <h4>ICO Token (Supply and Demand)</h4>
                            </div>
                            <div className="card-body bar-chart">
                                <BarChartOne/>
                            </div>
                        </div>
                    </div>
                    <div className="col-lg-4">
                        <div className="card single-chart">
                            <div className="card-header">
                                <h4>Progressive Crypto</h4>
                            </div>
                            <div className="card-body">
                                <PieChartOne/>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="row">
                    <div className="col-lg-8">
                        <div className="card single-chart">
                            <div className="card-header">
                                <h4>Balance Statistics</h4>
                            </div>
                            <div className="card-body">
                                <LineChartOne/>
                            </div>
                        </div>
                    </div>
                    <div className="col-lg-4">
                        <div className="card single-chart">
                            <div className="card-header">
                                <h4>ICO Distribution</h4>
                            </div>
                            <div className="card-body">
                                <PieChartTwo/>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
