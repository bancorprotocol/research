import React from 'react'
import PieChartTwo from "../components/charts/pie_chart_two";

export default function CoinWidgets() {
    return (
        <>
            <div className="row justify-content-between align-items-center">
                <div className="col-lg-6">
                    <h2 className="page-title">Your Currencies</h2>
                    <p>The currencies you have purchased are here.</p>
                    <div className="currency-icons">
                        <i className="cc BTC"></i>
                        <i className="cc ETH"></i>
                        <i className="cc XRP"></i>
                        <i className="cc NEO-alt"></i>
                        <i className="cc LTC"></i>
                        <i className="fa fa-plus"></i>
                    </div>
                </div>
                <div className="col-lg-4">
                    <div id="doughutChart">
                        <PieChartTwo />
                    </div>
                </div>
            </div>
            <div className="row m-t-25">
                <div className="col-lg-3">
                    <div className="card currency-card-rounded">
                        <div className="card-body rounded bitcoin">
                            <div className="currency-card--icon pull-right">
                                <i className="cc BTC-alt" title="BTC"></i>
                            </div>
                            <h4>Bitcoin</h4>
                            <h2><span>1.765</span> BTC</h2>
                            <p>Brought Rate: 25%</p>
                            <div className="progress">
                                <div className="progress-bar" role="progressbar" style={{ width: "25%" }}></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="col-lg-3">
                    <div className="card currency-card-rounded">
                        <div className="card-body rounded ethereum">
                            <div className="currency-card--icon pull-right">
                                <i className="cc ETH-alt" title="ETH"></i>
                            </div>
                            <h4>Ethereum</h4>
                            <h2><span>1.765</span> BTC</h2>
                            <p>Brought Rate: 50%</p>
                            <div className="progress">
                                <div className="progress-bar" role="progressbar" style={{ width: "50%" }}></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="col-lg-3">
                    <div className="card currency-card-rounded">
                        <div className="card-body rounded ripple">
                            <div className="currency-card--icon pull-right">
                                <i className="cc XRP-alt" title="XRP"></i>
                            </div>
                            <h4>Ripple</h4>
                            <h2><span>1.765</span> BTC</h2>
                            <p>Brought Rate: 75%</p>
                            <div className="progress">
                                <div className="progress-bar" role="progressbar" style={{ width: "75%" }}></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="col-lg-3">
                    <div className="card currency-card-rounded">
                        <div className="card-body rounded litecoin">
                            <div className="currency-card--icon pull-right">
                                <i className="cc LTC-alt" title="LTC"></i>
                            </div>
                            <h4>Litecoin</h4>
                            <h2><span>1.765</span> BTC</h2>
                            <p>Brought Rate: 45%</p>
                            <div className="progress">
                                <div className="progress-bar" role="progressbar" style={{ width: "45%" }}></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}
