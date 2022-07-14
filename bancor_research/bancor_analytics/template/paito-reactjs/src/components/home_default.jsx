import React from 'react';
import BarChartTwo from "./charts/bar_chart_two";
import CustomAccordion from "../components/custom/custom_accordion";
import CoinWidgets from "../components/coin_widgets";

export default function HomeDefault() {

    return (
        <>
            <div className="content-body">
                <div className="container-fluid">
                    <CoinWidgets/>
                    <div className="row m-t-25">
                        <div className="col-lg-4">
                            <CustomAccordion 
                              title="Current Pricing" 
                              eventKey="pricing" 
                              className="table-data crypto-price-card"
                              >
                                <div className="pricing-wrapper">
                                    <table className="table m-b-0">
                                        <thead>
                                            <tr className="search-block">
                                                <th scope="col">Show 15</th>
                                                <th colSpan="2" scope="col">
                                                    <span>Search</span>
                                                    <input placeholder="Search" type="search" />
                                                </th>
                                            </tr>
                                            <tr>
                                                <th scope="col">Coins</th>
                                                <th scope="col">Prices</th>
                                                <th scope="col">Change %</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>BTC</td>
                                                <td>$12,623.40</td>
                                                <td className="change">
                                                    <i className="fa fa-angle-up"></i>
                                                    <span>+6.50%</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td>ETH</td>
                                                <td>$12,623.40</td>
                                                <td className="change">
                                                    <i className="fa fa-angle-up"></i>
                                                    <span>+6.50%</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td>LTC</td>
                                                <td>$12,623.40</td>
                                                <td className="change">
                                                    <i className="fa fa-angle-up"></i>
                                                    <span>+6.50%</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td>XRP</td>
                                                <td>$12,623.40</td>
                                                <td className="change">
                                                    <i className="fa fa-angle-up"></i>
                                                    <span>+6.50%</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td>DASH</td>
                                                <td>$12,623.40</td>
                                                <td className="change">
                                                    <i className="fa fa-angle-up"></i>
                                                    <span>+6.50%</span>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </CustomAccordion>
                        </div>
                        <div className="col-lg-8">
                            <CustomAccordion
                                title="Currency Chart"
                                eventKey="chart"
                                className="crypto-chart-card"
                            >
                                <div className="chart-wrapper">
                                    <BarChartTwo />
                                </div>
                            </CustomAccordion>
                        </div>
                    </div>

                    <div className="row m-t-25">
                        <div className="col-lg-3">
                            <CustomAccordion
                                title=" Live Crypto"
                                eventKey="live_crypto"
                                className="crypto-price-card"
                            >
                                <ul className="m-b-0">
                                    <li>
                                        <span className="currency-name BTC">
                                            BTC
                                        </span>
                                        <span className="currency-status pull-right">
                                            $8.114
                                        <i className="fa fa-angle-down"></i>
                                        </span>
                                    </li>
                                    <li>
                                        <span className="currency-name ETH">
                                            ETH
                                        </span>
                                        <span className="currency-status pull-right">
                                            $8.114
                                        <i className="fa fa-angle-up"></i>
                                        </span>
                                    </li>
                                    <li>
                                        <span className="currency-name XRP">
                                            XRP
                                        </span>
                                        <span className="currency-status pull-right">
                                            $8.114
                                        <i className="fa fa-angle-up"></i>
                                        </span>
                                    </li>
                                    <li>
                                        <span className="currency-name NEO">
                                            NEO
                                        </span>
                                        <span className="currency-status pull-right">
                                            $8.114
                                         <i className="fa fa-angle-down"></i>
                                        </span>
                                    </li>
                                    <li>
                                        <span className="currency-name">
                                            BTC
                                        </span>
                                        <span className="currency-status pull-right">
                                            $8.114
                                            <i className="fa fa-angle-up"></i>
                                        </span>
                                    </li>
                                </ul>
                            </CustomAccordion>
                        </div>
                        <div className="col-lg-3">
                            <CustomAccordion
                                title="Transfer Coin"
                                eventKey="transfer_coin"
                                className="crypto-transfer-card"
                            >
                                <form action="#">
                                    <div className="input-group m-b-30">
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                $
                                            </div>
                                        </div>
                                        <input type="text" className="form-control" name="choose_coin" placeholder="Enter Amount" required />
                                        <span className="input-dropdown">
                                            <select name="" id="">
                                                <option value="BTC">BTC</option>
                                                <option value="ETC">ETC</option>
                                                <option value="XHR">XHR</option>
                                            </select>
                                        </span>
                                    </div>
                                    <div className="input-group m-b-30">
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                $
                                            </div>
                                        </div>
                                        <input type="text" name="coin_amount" className="form-control" required />
                                    </div>
                                    <button className="btn btn-success button" type="submit">Send</button>
                                </form>
                            </CustomAccordion>

                        </div>
                        <div className="col-lg-3">
                            <CustomAccordion
                                title="Walet Address"
                                eventKey="walet_address"
                                className="walet-address-card"
                            >
                                <div className="card-body-2">
                                    <h6>
                                        Bitcoin wallet address
                                    </h6>
                                    <div className="input-group m-b-20">
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                <i className="cc BTC" aria-hidden="true"></i>
                                            </div>
                                        </div>
                                        <input type="text" className="form-control walet-address" />
                                        <span className="input-group-addon">
                                            Copy
                                        </span>
                                    </div>
                                    <h6 className="m-t-20">Ethereum Walet Address</h6>
                                    <div className="input-group m-b-20">
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                <i className="cc ETC" aria-hidden="true"></i>
                                            </div>
                                        </div>
                                        <input type="text" className="form-control walet-address" />
                                        <span className="input-group-addon" id="">
                                            Copy
                                        </span>
                                    </div>
                                    <h6 className="m-t-20">Ripple Walet Address</h6>
                                    <div className="input-group">
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                <i className="cc XRP" aria-hidden="true"></i>
                                            </div>
                                        </div>
                                        <input type="text" className="form-control walet-address" />
                                        <span className="input-group-addon">
                                            Copy
                                        </span>
                                    </div>
                                </div>
                                <div className="walet-direction">
                                    <h4 className="mb-0">
                                        <a href="">Go to Wallet</a>
                                    </h4>
                                </div>
                            </CustomAccordion>
                        </div>

                        <div className="col-lg-3">
                            <CustomAccordion
                                title="Recent Transactions"
                                eventKey="transactions"
                                className="crypto-price-card"
                            >
                                <table className="table m-b-0">
                                    <thead>
                                        <tr>
                                            <th scope="col">Price</th>
                                            <th scope="col">Amount</th>
                                            <th scope="col">When</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>12,623.40</td>
                                            <td>$12,623.40</td>
                                            <td className="change">
                                                <span>21 min age</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>12,623.40</td>
                                            <td>$12,623.40</td>
                                            <td className="change">
                                                <span>21 min age</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>12,623.40</td>
                                            <td>$12,623.40</td>
                                            <td className="change">
                                                <span>21 min age</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>12,623.40</td>
                                            <td>$12,623.40</td>
                                            <td className="change">
                                                <span>21 min age</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>12,623.40</td>
                                            <td>$12,623.40</td>
                                            <td className="change">
                                                <span>21 min age</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td colSpan="3">
                                                <div className="walet-direction">
                                                    <h4 className="mb-0 text-center">
                                                        <a href="">Go to Trade</a>
                                                    </h4>
                                                </div>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </CustomAccordion>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}
