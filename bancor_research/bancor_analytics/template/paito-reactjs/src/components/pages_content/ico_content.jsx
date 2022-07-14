import React from 'react';
import CustomAccordion from "../custom/custom_accordion";
import PieChartOne from "../charts/pie_chart_one";
import BarChartOne from "../charts/bar_chart_one";
export default function IcoContent() {
    return (
        <div className="content-body">
            <div className="container-fluid">
                <div className="row">
                    <div className="col-lg-6">
                        <h2 className="page-title">ICO Dashboard</h2>
                    </div>
                </div>
            </div>

            <div className="ico-section">
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-lg-8">
                            <CustomAccordion
                                title="ICO Distributions"
                                eventKey="ico_dist_chart"
                                className="ico-dist-card mb-4"
                            >
                                <div className="crypto-ico-chart">
                                    <BarChartOne />
                                </div>
                            </CustomAccordion>
                        </div>
                        <div className="col-lg-4 mb-md-4">
                            <CustomAccordion
                                title="Crypto Average"
                                eventKey="crypto_avg"
                                className="crypto-avg-card"
                            >
                             <div className="pie-chart-wrapper">
                                <PieChartOne />
                             </div>
                            </CustomAccordion>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-lg-4"> 
                            <CustomAccordion
                              title="Live my Crypto Prices"
                              eventKey="live_crypto"
                              className="crypto-price-card"
                            >
                                <div id="crypto-price">
                                    <div className="card-body">
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
                                    </div>
                                </div>
                            </CustomAccordion>
                        </div>
                        <div className="col-lg-8">
                            <CustomAccordion
                                title="Buy Token"
                                eventKey="buy_token"
                                className="table-data"
                            >
                                <div id="buy-token">
                                    <div className="card-body">
                                        <form className="form buy-token-form">
                                            <div className="ico-token token">
                                                <label htmlFor="ico_token">ICO Token</label>
                                                <input type="text" className="form-control" id="ico_token" placeholder="2000" />
                                            </div>
                                            <div className="balance token">
                                                <label htmlFor="eth_coin">ETH</label>
                                                <input type="text" className="form-control" id="eth_coin" placeholder="1" />
                                            </div>
                                            <div className="currency token">
                                                <label htmlFor="">Coin</label>
                                                <select className="custom-select">
                                                    <option value="0">ETH</option>
                                                    <option value="1">BTC</option>
                                                    <option value="2">XHR</option>
                                                </select>
                                            </div>
                                            <div className="w-address token">
                                                <label htmlFor="wl_address">Walet Address</label>
                                                <input type="text" className="form-control" id="wl_address" />
                                            </div>
                                            <div className="submit-btn token mt-2">
                                                <button type="submit" className="btn btn-success">Submit</button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </CustomAccordion>
                            <CustomAccordion
                                title="Recent Transactions"
                                eventKey="transactions"
                                className="table-data"
                            >
                                <div id="table-two" className="table-responsive">
                                    <table className="table m-b-0">
                                        <thead>
                                            <tr>
                                                <th scope="col">Status</th>
                                                <th scope="col">Date</th>
                                                <th scope="col">Amount</th>
                                                <th scope="col">Value</th>
                                                <th scope="col">Currency</th>
                                                <th scope="col">Token</th>
                                                <th scope="col">Details</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td className="status">
                                                    <span>
                                                        Pending
                                                    </span>
                                                </td>
                                                <td>13-02-18</td>
                                                <td className="amount">Deposit</td>
                                                <td className="value">5,3411</td>
                                                <td>ETH</td>
                                                <td className="token">3201</td>
                                                <td className="details">Deposit to your Balance</td>
                                            </tr>
                                            <tr>
                                                <td className="status">
                                                    <span>
                                                        Pending
                                                    </span>
                                                </td>
                                                <td>13-02-18</td>
                                                <td className="amount">Deposit</td>
                                                <td className="value">5,3411</td>
                                                <td>ETH</td>
                                                <td className="token">3201</td>
                                                <td className="details">Deposit to your Balance</td>
                                            </tr>
                                            <tr>
                                                <td className="status">
                                                    <span>
                                                        Pending
                                                    </span>
                                                </td>
                                                <td>13-02-18</td>
                                                <td className="amount">Deposit</td>
                                                <td className="value">5,3411</td>
                                                <td>ETH</td>
                                                <td className="token">3201</td>
                                                <td className="details">Deposit to your Balance</td>
                                            </tr>
                                            <tr>
                                                <td className="status">
                                                    <span>
                                                        Pending
                                                    </span>
                                                </td>
                                                <td>13-02-18</td>
                                                <td className="amount">Deposit</td>
                                                <td className="value">5,3411</td>
                                                <td>ETH</td>
                                                <td className="token">3201</td>
                                                <td className="details">Deposit to your Balance</td>
                                            </tr>
                                            <tr>
                                                <td className="status">
                                                    <span>
                                                        Pending
                                                    </span>
                                                </td>
                                                <td>13-02-18</td>
                                                <td className="amount">Deposit</td>
                                                <td className="value">5,3411</td>
                                                <td>ETH</td>
                                                <td className="token">3201</td>
                                                <td className="details">Deposit to your Balance</td>
                                            </tr>
                                            <tr>
                                                <td className="status">
                                                    <span>
                                                        Pending
                                                    </span>
                                                </td>
                                                <td>13-02-18</td>
                                                <td className="amount">Deposit</td>
                                                <td className="value">5,3411</td>
                                                <td>ETH</td>
                                                <td className="token">3201</td>
                                                <td className="details">Deposit to your Balance</td>
                                            </tr>
                                            <tr>
                                                <td className="status">
                                                    <span>
                                                        Pending
                                                    </span>
                                                </td>
                                                <td>13-02-18</td>
                                                <td className="amount">Deposit</td>
                                                <td className="value">5,3411</td>
                                                <td>ETH</td>
                                                <td className="token">3201</td>
                                                <td className="details">Deposit to your Balance</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </CustomAccordion>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    )
}
