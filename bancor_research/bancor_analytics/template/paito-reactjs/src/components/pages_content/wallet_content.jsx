import React from 'react';
import CoinWidgets from "../coin_widgets";
import CustomAccordion from "../custom/custom_accordion";

export default function WalletContent() {
    return (
        <div className="content-body">
            <div className="container-fluid">
                <div className="coin-widgets-wrapper m-b-30">
                    <CoinWidgets />
                </div>
                
                <div className="row">
                    <div className="col-lg-4 col-md-6 walet-info-card">
                        <CustomAccordion title="Bitcoin" eventKey="bitcoin_key" className="accordion__walet">
                            <div className="walet-info-one">
                                <div className="card-body-2">
                                    <div className="walet-title">
                                        <i className="cc BTC currency-card--icon pull-left" title="BTC"></i>
                                        <h6>Bitcoin</h6>
                                        <p>1 BTC : $ 13.625 USD</p>
                                    </div>
                                    <div className="walet-details">
                                        <div className="input-group m-b-30">
                                            <div className="input-group-prepend">
                                                <div className="input-group-text">
                                                    <i className="fa fa-credit-card-alt" aria-hidden="true"></i>
                                                </div>
                                            </div>
                                            <input type="text" className="form-control walet-address" value="Mxs123PWid6YZX96" readOnly/>
                                            <span className="input-group-addon">
                                                Copy
                                            </span>
                                        </div>
                                        <div className="walet-status">
                                            <ul>
                                                <li>
                                                    Total selling:
                                                    <span> $ 54,653.10</span>
                                                </li>
                                                <li>
                                                    Total buying:
                                                    <span>$ 234,653.15</span>
                                                </li>
                                                <li>
                                                    Balance:
                                                    <span>1.254,653 BTC</span>
                                                </li>
                                                <li>
                                                    Balance in USD:
                                                    <span>$ 15,384,653.15 USD</span>
                                                </li>
                                            </ul>
                                            <button className="btn btn-success btn-block m-t-30">Withdraw</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </CustomAccordion>
                    </div>
                    <div className="col-lg-4 col-md-6 walet-info-card">
                        <CustomAccordion title="Ethereum" eventKey="ethereum_key" className="accordion__walet">
                            <div className="walet-info-two">
                                <div className="card-body-2">
                                    <div className="walet-title">
                                        <i className="cc ETH currency-card--icon pull-left" title="ETH"></i>
                                        <h6>Ethereum</h6>
                                        <p>1 ETH : $ 13.625 USD</p>
                                    </div>
                                    <div className="walet-details">
                                        <div className="input-group m-b-30">
                                            <div className="input-group-prepend">
                                                <div className="input-group-text">
                                                    <i className="fa fa-credit-card-alt" aria-hidden="true"></i>
                                                </div>
                                            </div>
                                            <input type="text" className="form-control walet-address" value="Mxs123PWid6YZX96" readOnly />
                                            <span className="input-group-addon">
                                                Copy
                                            </span>
                                        </div>
                                        <div className="walet-status">
                                            <ul>
                                                <li>
                                                    Total selling:
                                                    <span> $ 54,653.10</span>
                                                </li>
                                                <li>
                                                    Total buying:
                                                   <span>$ 234,653.15</span>
                                                </li>
                                                <li>
                                                    Balance:
                                                   <span>1.254,653 BTC</span>
                                                </li>
                                                <li>
                                                    Balance in USD:
                                                    <span>$ 15,384,653.15 USD</span>
                                                </li>
                                            </ul>
                                            <button className="btn btn-success btn-block m-t-30">Withdraw</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </CustomAccordion>
                    </div>
                    <div className="col-lg-4 col-md-6 walet-info-card">
                        <CustomAccordion title="Ripple" eventKey="ripple_key" className="accordion__walet">
                            <div className="walet-info-three">
                                <div className="card-body-2">
                                    <div className="walet-title">
                                        <i className="cc XRP currency-card--icon pull-left" title="XRP"></i>
                                        <h6>Ripple</h6>
                                        <p>1 XRP : $ 13.625 USD</p>
                                    </div>
                                    <div className="walet-details">
                                        <div className="input-group m-b-30">
                                            <div className="input-group-prepend">
                                                <div className="input-group-text">
                                                    <i className="fa fa-credit-card-alt" aria-hidden="true"></i>
                                                </div>
                                            </div>
                                            <input type="text" className="form-control walet-address" value="Mxs123PWid6YZX96" readOnly />
                                            <span className="input-group-addon">
                                                Copy
                                            </span>
                                        </div>
                                        <div className="walet-status">
                                            <ul>
                                                <li>
                                                    Total selling:
                                                    <span> $ 54,653.10</span>
                                                </li>
                                                <li>
                                                    Total buying:
                                                   <span>$ 234,653.15</span>
                                                </li>
                                                <li>
                                                    Balance:
                                                   <span>1.254,653 BTC</span>
                                                </li>
                                                <li>
                                                    Balance in USD:
                                                    <span>$ 15,384,653.15 USD</span>
                                                </li>
                                            </ul>
                                            <button className="btn btn-success btn-block m-t-30">Withdraw</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </CustomAccordion>
                    </div>
                    <div className="col-lg-4 col-md-6 walet-info-card">
                        <CustomAccordion title="Litecoin" eventKey="litecoin_key" className="accordion__walet">
                            <div className="walet-info-one">
                                <div className="card-body-2">
                                    <div className="walet-title">
                                        <i className="cc LTC-alt currency-card--icon pull-left" title="LTC-alt"></i>
                                        <h6>Litecoin</h6>
                                        <p>1 LTC : $ 13.625 USD</p>
                                    </div>
                                    <div className="walet-details">
                                        <div className="input-group m-b-30">
                                            <div className="input-group-prepend">
                                                <div className="input-group-text">
                                                    <i className="fa fa-credit-card-alt" aria-hidden="true"></i>
                                                </div>
                                            </div>
                                            <input type="text" className="form-control walet-address" value="Mxs123PWid6YZX96" readOnly />
                                            <span className="input-group-addon">
                                                Copy
                                           </span>
                                        </div>
                                        <div className="walet-status">
                                            <ul>
                                                <li>
                                                    Total selling:
                                                    <span> $ 54,653.10</span>
                                                </li>
                                                <li>
                                                    Total buying:
                                                   <span>$ 234,653.15</span>
                                                </li>
                                                <li>
                                                    Balance:
                                                   <span>1.254,653 BTC</span>
                                                </li>
                                                <li>
                                                    Balance in USD:
                                                   <span>$ 15,384,653.15 USD</span>
                                                </li>
                                            </ul>
                                            <button className="btn btn-success btn-block m-t-30">Withdraw</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </CustomAccordion>
                    </div>
                    <div className="col-lg-4 col-md-6 walet-info-card">
                        <CustomAccordion title="NEO" eventKey="neo_coin_key" className="accordion__walet">
                            <div className="card walet-info-card rounded-0">
                                <div className="walet-info-one" className="collapse show">
                                    <div className="card-body-2">
                                        <div className="walet-title">
                                            <i className="cc NEO-alt currency-card--icon pull-left" title="NEO-alt"></i>
                                            <h6>NEO</h6>
                                            <p>1 NEO : $ 13.625 USD</p>
                                        </div>
                                        <div className="walet-details">
                                            <div className="input-group m-b-30">
                                                <div className="input-group-prepend">
                                                    <div className="input-group-text">
                                                        <i className="fa fa-credit-card-alt" aria-hidden="true"></i>
                                                    </div>
                                                </div>
                                                <input type="text" className="form-control walet-address" value="Mxs123PWid6YZX96" readOnly />
                                                <span className="input-group-addon">
                                                    Copy
                                               </span>
                                            </div>
                                            <div className="walet-status">
                                                <ul>
                                                    <li>
                                                        Total selling:
                                                       <span> $ 54,653.10</span>
                                                    </li>
                                                    <li>
                                                        Total buying:
                                                       <span>$ 234,653.15</span>
                                                    </li>
                                                    <li>
                                                        Balance:
                                                        <span>1.254,653 BTC</span>
                                                    </li>
                                                    <li>
                                                        Balance in USD:
                                                       <span>$ 15,384,653.15 USD</span>
                                                    </li>
                                                </ul>
                                                <button className="btn btn-success btn-block m-t-30">Withdraw</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </CustomAccordion>
                    </div>
                    <div className="col-lg-4 col-md-6 walet-info-card">
                        <CustomAccordion title="Monero" eventKey="monero_coin_key" className="accordion__walet">
                            <div className="walet-info-one" className="collapse show">
                                <div className="card-body-2">
                                    <div className="walet-title">
                                        <i className="cc XMR currency-card--icon pull-left" title="XMR"></i>
                                        <h6>Monero</h6>
                                        <p>1 XMR : $ 13.625 USD</p>
                                    </div>
                                    <div className="walet-details">
                                        <div className="input-group m-b-30">
                                            <div className="input-group-prepend">
                                                <div className="input-group-text">
                                                    <i className="fa fa-credit-card-alt" aria-hidden="true"></i>
                                                </div>
                                            </div>
                                            <input type="text" className="form-control walet-address" value="Mxs123PWid6YZX96" readOnly />
                                            <span className="input-group-addon">
                                                Copy
                                            </span>
                                        </div>
                                        <div className="walet-status">
                                            <ul>
                                                <li>
                                                    Total selling:
                                                    <span> $ 54,653.10</span>
                                                </li>
                                                <li>
                                                    Total buying:
                                                    <span>$ 234,653.15</span>
                                                </li>
                                                <li>
                                                    Balance:
                                                   <span>1.254,653 BTC</span>
                                                </li>
                                                <li>
                                                    Balance in USD:
                                                    <span>$ 15,384,653.15 USD</span>
                                                </li>
                                            </ul>
                                            <button className="btn btn-success btn-block m-t-30">Withdraw</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </CustomAccordion>
                    </div>
                </div>
            </div>
        </div>
    )
}
