import React from 'react';
import CustomAccordion from "../custom/custom_accordion";
import exchangeImg from "../../../src/assets/images/currency_exchange.jpg";

export default function ExchangeContent() {
    return (
        <div className="content-body">
            <div className="container-fluid">
                <div className="row">
                    <div className="col-lg-12">
                        <h2 className="page-title">Currency Exchange</h2>
                    </div>
                </div>
            </div>

            <div className="currency-hero-area" style={{ backgroundImage: `url(${exchangeImg})`}}>
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-lg-8 offset-lg-2">
                            <div className="parapraph-desc text-black">
                                <h1>Buy and sell coins at the cryptopic without additional fees.</h1>
                                <p>Proin non tortor pharetra nisi ultricies rhoncus. Quisque posuere ut mi et viverra. Nunc lorem odio, aliquam vel ipsum vel, posuere posuere augue. Sed convallis dui ut erat consequat, in sodales sapien ornare.</p>
                            </div>
                            <div className="exchange-input">
                                <div className="input-group m-b-30">
                                    <input type="text" className="form-control" placeholder="0.0231" />
                                    <span className="input-dropdown">
                                        <select name="selected_coin">
                                            <option value="BTC">BTC</option>
                                            <option value="ETC">ETC</option>
                                            <option value="XHR">XHR</option>
                                        </select>
                                    </span>
                                </div>
                                <div className="exchange-icon">
                                    <i className="fa fa-exchange"></i>
                                </div>
                                <div className="input-group m-b-30">
                                    <input type="text" className="form-control" placeholder="0.0231" />
                                    <span className="input-dropdown">
                                        <select name="select_coin">
                                            <option value="BTC">BTC</option>
                                            <option value="ETC">ETC</option>
                                            <option value="XHR">XHR</option>
                                        </select>
                                    </span>
                                </div>
                            </div>
                            <div className="exchange-button">
                                <button className="custom-btn btn-hover">Exchange Now</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="currency-cards">
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-lg-4 col-md-6">
                            <CustomAccordion
                              title="Bitcoin"
                              eventKey="bitcoin_currency"
                              className="accordion__currency"
                            >
                                <div  className="accordion-btc">
                                    <div className="card-body-2">
                                        <div className="currency-card--title">
                                            <i className="cc BTC currency-card--icon pull-left" title="BTC"></i>
                                            <h2>Bitcoin BTC</h2>
                                        </div>
                                        <div className="currency-card--rates">
                                            <div className="currency-card--increment">
                                                0.00000231
                                            </div>
                                            <div className="currency-card--change text-right">
                                                +1.35%
                                            </div>
                                            <div className="currency-card--price">
                                                $0.02
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </CustomAccordion>
                        </div>

                        <div className="col-lg-4 col-md-6">
                            <CustomAccordion
                                title="Ethereum"
                                eventKey="ethereum_currency"
                                className="accordion__currency"
                            >
                                <div className="card-body-2">
                                    <div className="currency-card--title">
                                        <i className="cc ETC-alt currency-card--icon pull-left" title="ETC"></i>
                                        <h2>Ethereum ETH</h2>
                                    </div>
                                    <div className="currency-card--rates">
                                        <div className="currency-card--increment">
                                            0.00000231
                                        </div>
                                        <div className="currency-card--change text-right">
                                            +1.35%
                                        </div>
                                        <div className="currency-card--price">
                                            $0.02
                                        </div>
                                    </div>
                                </div>
                            </CustomAccordion>
                        </div>

                        <div className="col-lg-4 col-md-6">
                            <CustomAccordion
                                title="Ripple"
                                eventKey="ripple_currency"
                                className="accordion__currency"
                            >
                                <div className="card-body-2">
                                    <div className="currency-card--title">
                                        <i className="cc XRP currency-card--icon pull-left" title="XRP"></i>
                                        <h2>Ripple XRP</h2>
                                    </div>
                                    <div className="currency-card--rates">
                                        <div className="currency-card--increment">
                                            0.00000231
                                        </div>
                                        <div className="currency-card--change text-right">
                                            +1.35%
                                        </div>
                                        <div className="currency-card--price">
                                            $0.02
                                        </div>
                                    </div>
                                </div>
                            </CustomAccordion>
                        </div>

                        <div className="col-lg-4 col-md-6">
                            <CustomAccordion
                                title="Litecoin"
                                eventKey="litecoin_currency"
                                className="accordion__currency"
                            >
                                <div className="card-body-2">
                                    <div className="currency-card--title">
                                        <i className="cc LTC currency-card--icon pull-left" title="LTC"></i>
                                        <h2>
                                            Litecoin LTC
                                                </h2>
                                    </div>
                                    <div className="currency-card--rates">
                                        <div className="currency-card--increment">
                                            0.00000231
                                                </div>
                                        <div className="currency-card--change text-right">
                                            +1.35%
                                                </div>
                                        <div className="currency-card--price">
                                            $0.02
                                                </div>
                                    </div>
                                </div>
                            </CustomAccordion>
                        </div>

                        <div className="col-lg-4 col-md-6">
                            <CustomAccordion
                                title="NEO"
                                eventKey="neo_currency"
                                className="accordion__currency"
                            >
                                <div className="card-body-2">
                                    <div className="currency-card--title">
                                        <i className="cc NEO-alt currency-card--icon pull-left" title="ETC"></i>
                                        <h2>
                                            Neo NEO
                                        </h2>
                                    </div>
                                    <div className="currency-card--rates">
                                        <div className="currency-card--increment">
                                            0.00000231
                                        </div>
                                        <div className="currency-card--change text-right">
                                            +1.35%
                                        </div>
                                        <div className="currency-card--price">
                                            $0.02
                                        </div>
                                    </div>
                                </div>
                            </CustomAccordion>
                        </div>

                        <div className="col-lg-4 col-md-6">
                            <CustomAccordion
                                title="Monero"
                                eventKey="monero_currency"
                                className="accordion__currency"
                            >
                                <div className="card-body-2">
                                    <div className="currency-card--title">
                                        <i className="cc XMR currency-card--icon pull-left" title="XMR"></i>
                                        <h2>Monero XMR</h2>
                                    </div>
                                    <div className="currency-card--rates">
                                        <div className="currency-card--increment">
                                            0.00000231
                                        </div>
                                        <div className="currency-card--change text-right">
                                            +1.35%
                                        </div>
                                        <div className="currency-card--price">
                                            $0.02
                                        </div>
                                    </div>
                                </div>
                            </CustomAccordion>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    )
}
