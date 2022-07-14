import React from 'react';
import CustomAccordion from "../custom/custom_accordion";

export default function BuySellContent() {
    return (
        <div className="content-body">
            <div className="container-fluid">
                <div className="row">
                    <div className="col-lg-12">
                        <h2 className="page-title">Buy and Sell</h2>
                    </div>
                </div>
            </div>

            <div className="tables-section">
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-lg-4 m-b-30">
                            <CustomAccordion
                              title="Buy cryptocurrency"
                              eventKey="buy_crypto"
                              className="crypto-card"
                            >
                                <div className="card-wrapper">
                                    <h6>
                                        Select the Crypto Currency
                                        <span>‘Minimum Value 0.001 BTC’</span>
                                    </h6>
                                    <div className="input-group">
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                <i className="cc BTC"></i>
                                            </div>
                                        </div>
                                        <select className="custom-select">
                                            <option value="1">Bitcoin</option>
                                            <option value="2">Ethereum</option>
                                            <option value="3">Repple</option>
                                        </select>
                                    </div>
                                    <h6 className="m-t-25">Choose Payment Method</h6>
                                    <div className="input-group">
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                <i className="icofont icofont-visa"></i>
                                            </div>
                                        </div>
                                        <select className="custom-select">
                                            <option value="1">Visa</option>
                                            <option value="1">Master</option>
                                        </select>
                                    </div>
                                    <h6 className="m-t-25">Walet Address</h6>
                                    <div className="input-group">
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                <i className="icofont icofont-visa"></i>
                                            </div>
                                        </div>
                                        <input type="text" className="form-control" />
                                    </div>
                                    <h6 className="m-t-25">Exchange Operation</h6>
                                    <div className="input-group">
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                <i className="icofont icofont-visa"></i>
                                            </div>
                                        </div>
                                        <input type="text" className="form-control" placeholder="Exchange Amount" />
                                        <div className="exchamge-icon p-2">
                                            <i className="fa fa-exchange"></i>
                                        </div>
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                <i className="icofont icofont-visa"></i>
                                            </div>
                                        </div>
                                        <input type="text" className="form-control" placeholder="Exchange Amount" />
                                    </div>
                                    <button className="btn btn-success m-t-25">Buy Cryptocurrencies</button>
                                </div>
                            </CustomAccordion>
                        </div>
                        <div className="col-lg-4 m-b-30">
                            <CustomAccordion
                                title="Buy cryptocurrency"
                                eventKey="buy_crypto_2"
                                className="crypto-card"
                            >
                                <div className="card-wrapper">
                                    <h6>
                                        Select the Crypto Currency
                                        <span>‘Minimum Value 0.001 BTC’</span>
                                    </h6>
                                    <div className="input-group">
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                <i className="cc BTC"></i>
                                            </div>
                                        </div>
                                        <select className="custom-select">
                                            <option value="1">Bitcoin</option>
                                            <option value="2">Ethereum</option>
                                            <option value="3">Repple</option>
                                        </select>
                                    </div>
                                    <h6 className="m-t-25">Choose Payment Method</h6>
                                    <div className="input-group">
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                <i className="icofont icofont-visa"></i>
                                            </div>
                                        </div>
                                        <select className="custom-select">
                                            <option value="1">Visa</option>
                                            <option value="1">Master</option>
                                        </select>
                                    </div>
                                    <h6 className="m-t-25">Walet Address</h6>
                                    <div className="input-group">
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                <i className="icofont icofont-visa"></i>
                                            </div>
                                        </div>
                                        <input type="text" className="form-control" />
                                    </div>
                                    <h6 className="m-t-25">Exchange Operation</h6>
                                    <div className="input-group">
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                <i className="icofont icofont-visa"></i>
                                            </div>
                                        </div>
                                        <input type="text" className="form-control" placeholder="Exchange Amount" />
                                        <div className="exchamge-icon p-2">
                                            <i className="fa fa-exchange"></i>
                                        </div>
                                        <div className="input-group-prepend">
                                            <div className="input-group-text">
                                                <i className="icofont icofont-visa"></i>
                                            </div>
                                        </div>
                                        <input type="text" className="form-control" placeholder="Exchange Amount" />
                                    </div>
                                    <button className="btn btn-success m-t-25">Buy Cryptocurrencies</button>
                                </div>
                            </CustomAccordion>
                        </div>
                        <div className="col-lg-4 m-b-30">
                            <CustomAccordion
                                title="Walet Address"
                                eventKey="crypto_walet"
                                className="walet-address-card"
                            >
                                <div id="wallet-address">
                                    <div className="card-wrapper">
                                        <h6>Bitcoin wallet address</h6>
                                        <div className="input-group m-b-30">
                                            <div className="input-group-prepend">
                                                <div className="input-group-text">
                                                    <i className="cc BTC" aria-hidden="true"></i>
                                                </div>
                                            </div>
                                            <input type="text" className="form-control walet-address" />
                                            <span className="input-group-addon" id="">
                                                Copy
                                            </span>
                                        </div>
                                        <h6 className="m-t-25">Ethereum Walet Address</h6>
                                        <div className="input-group m-b-30">
                                            <div className="input-group-prepend">
                                                <div className="input-group-text">
                                                    <i className="cc ETC" aria-hidden="true"></i>
                                                </div>
                                            </div>
                                            <input type="text" className="form-control walet-address" />
                                            <span className="input-group-addon">
                                                Copy
                                            </span>
                                        </div>
                                        <h6 className="m-t-25">Ripple Walet Address</h6>
                                        <div className="input-group m-b-30">
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
                                        <h6 className="m-t-25">Litecoin Walet Address</h6>
                                        <div className="input-group m-b-0">
                                            <div className="input-group-prepend">
                                                <div className="input-group-text">
                                                    <i className="cc LTC" aria-hidden="true"></i>
                                                </div>
                                            </div>
                                            <input type="text" className="form-control walet-address" />
                                            <span className="input-group-addon" id="">
                                                Copy
                                            </span>
                                        </div>
                                    </div>
                                    <div className="walet-direction">
                                        <h4 className="mb-0">
                                            <a href="#">Go to Wallet</a>
                                        </h4>
                                    </div>
                                </div>
                            </CustomAccordion>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-lg-6">
                            <CustomAccordion
                                title="Recent Buying Cryptocurrencies"
                                eventKey="recent_crypto"
                                className="table-data"
                            >
                                <div id="table-three">
                                    <table className="table m-b-0">
                                        <thead>
                                            <tr>
                                                <th scope="col">ID Number</th>
                                                <th scope="col">Trade Time</th>
                                                <th scope="col">Status</th>
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
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </CustomAccordion>
                        </div>
                        <div className="col-lg-6">
                            <CustomAccordion
                                title="Recent Selling Orders"
                                eventKey="recent_selling_crypto"
                                className="table-data"
                            >
                                <div id="table-three">
                                    <table className="table m-b-0">
                                        <thead>
                                            <tr>
                                                <th scope="col">ID Number</th>
                                                <th scope="col">Trade Time</th>
                                                <th scope="col">Status</th>
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
