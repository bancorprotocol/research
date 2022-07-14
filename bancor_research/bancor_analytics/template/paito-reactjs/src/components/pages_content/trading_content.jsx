import React from 'react';
import LineChartOne from "../charts/line_chart_one";
import LineChartTwo from "../charts/line_chart_two";
import CustomAccordion from "../custom/custom_accordion";
import CryptoLiveChart from "../charts/crypto_live_chart";

export default function TradingContent() {

    return (
        <div className="content-body">
            <div className="container-fluid">
                <CryptoLiveChart />
                <div className="row">
                    <div className="col-md-6">
                        <div className="card m-b-30">
                            <div className="card-body">
                                <h4 className="card-title">Bitcoin Rate</h4>
                                <div className="text-center">
                                    <LineChartOne/>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-6">
                        <div className="card m-b-30">
                            <div className="card-body">
                                <h4 className="card-title">Crypto Sales</h4>
                                  <LineChartTwo/>
                                </div>
                            </div>
                        </div>
                    </div>
                <div className="row">
                    <div className="col-lg-4">
                        <CustomAccordion
                            title="Transfer coins"
                            eventKey="transfer"
                            className="coin-transfer m-b-30"
                        >
                            <div className="card-body">
                                <div className="input-group m-b-30">
                                    <div className="input-group-prepend">
                                        <div className="input-group-text">
                                            $
                                            </div>
                                    </div>
                                    <input type="text" className="form-control" placeholder="Enter Amount" />
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
                                    <input type="text" className="form-control" />
                                </div>
                                <button className="btn btn-success button">Send</button>
                            </div>
                        </CustomAccordion>
                        <CustomAccordion
                            title="Live my Crypto Prices"
                            eventKey="live_crypto"
                            className="crypto-price-card"
                        >
                            <div className="card-body mt-4">
                                <ul>
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
                        </CustomAccordion>
                            </div>
                            <div className="col-lg-8">
                        <CustomAccordion
                            title="Recent Trading Activities"
                            eventKey="recent_trading"
                            className="table-data"
                        >
                            <div id="table-two" className="table-responsive">
                                <table className="table m-b-0">
                                    <thead>
                                        <tr>
                                            <th scope="col">ID Number</th>
                                            <th scope="col">Trade Time</th>
                                            <th scope="col">Status</th>
                                            <th scope="col">Last Trade</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>
                                                <span>ID Number </span>
                                                <span className="id">175896</span>
                                            </td>
                                            <td>04.40 am</td>
                                            <td>
                                                <span className="success">
                                                    Pending
                                                    </span>
                                            </td>
                                            <td className="last-trade">
                                                <i className="fa fa-angle-up"></i>
                                                <span> 0.00311 LTC</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <span>ID Number </span>
                                                <span className="id">175896</span>
                                            </td>
                                            <td>02.40 am</td>
                                            <td>
                                                <span className="success">
                                                    Complete
                                                    </span>
                                            </td>
                                            <td className="last-trade">
                                                <i className="fa fa-angle-up"></i>
                                                <span> 0.00311 BTC</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <span>ID Number </span>
                                                <span className="id">175896</span>
                                            </td>
                                            <td>01.40 am</td>
                                            <td>
                                                <span className="success">
                                                    Complete
                                                    </span>
                                            </td>
                                            <td className="last-trade">
                                                <i className="fa fa-angle-up"></i>
                                                <span> 0.00311 BTC</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <span>ID Number </span>
                                                <span className="id">175896</span>
                                            </td>
                                            <td>04.40 am</td>
                                            <td>
                                                <span className="success">
                                                    Pending
                                                    </span>
                                            </td>
                                            <td className="last-trade">
                                                <i className="fa fa-angle-up"></i>
                                                <span> 0.00311 ETH</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <span>ID Number </span>
                                                <span className="id">175896</span>
                                            </td>
                                            <td>05.40 am</td>
                                            <td>
                                                <span className="success">
                                                    Complete
                                                    </span>
                                            </td>
                                            <td className="last-trade">
                                                <i className="fa fa-angle-up"></i>
                                                <span> 0.00311 DASH</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <span>ID Number </span>
                                                <span className="id">175896</span>
                                            </td>
                                            <td>02.40 am</td>
                                            <td>
                                                <span className="success">
                                                    Complete
                                                    </span>
                                            </td>
                                            <td className="last-trade">
                                                <i className="fa fa-angle-up"></i>
                                                <span> 0.00311 NEO</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <span>ID Number </span>
                                                <span className="id">175896</span>
                                            </td>
                                            <td>03.40 am</td>
                                            <td>
                                                <span className="success">
                                                    Complete
                                                    </span>
                                            </td>
                                            <td className="last-trade">
                                                <i className="fa fa-angle-up"></i>
                                                <span> 0.00311 BTC</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <span>ID Number </span>
                                                <span className="id">175896</span>
                                            </td>
                                            <td>05.40 am</td>
                                            <td>
                                                <span className="success">
                                                    Pending
                                                    </span>
                                            </td>
                                            <td className="last-trade">
                                                <i className="fa fa-angle-up"></i>
                                                <span> 0.00311 XRP</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <span>ID Number </span>
                                                <span className="id">175896</span>
                                            </td>
                                            <td>04.40 am</td>
                                            <td>
                                                <span className="success">
                                                    Complete
                                                    </span>
                                            </td>
                                            <td className="last-trade">
                                                <i className="fa fa-angle-up"></i>
                                                <span> 0.00311 BTC</span>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </CustomAccordion>
                            </div>
                        </div>
                        
                    </div>
                    </div>
                 
    )
}
