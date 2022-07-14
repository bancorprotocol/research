import React from 'react';
export default function MarketcapContent() {
    return (
        <div className="content-body">
            <div className="container-fluid">
                <div className="row">
                    <div className="col-lg-12">
                        <h2 className="page-title">Marketcap</h2>
                    </div>
                </div>
            </div>
            <div className="marketcap-section">
                <div className="container-fluid">
                    <div className="row m-b-30">
                        <div className="col-lg-4 col-md-6">
                            <div className="card marketcap-currency rounded-5">
                                <div className="card-body">
                                    <div className="total-value">
                                        <h4>Marketcap</h4>
                                        <h2>$421,833,368,630.10</h2>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col-lg-4 col-md-6">
                            <div className="card marketcap-currency rounded-5">
                                <div className="card-body">
                                    <div className="total-value">
                                        <h4>Market Vlue</h4>
                                        <h2>$421,833,368,630.10</h2>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col-lg-4 col-md-6">
                            <div className="card marketcap-currency rounded-5">
                                <div className="card-body">
                                    <div className="total-value">
                                        <h4>Dominance</h4>
                                        <h2>$421,833,368,630.10</h2>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-lg-12">
                            <div className="marketcap-category-chart">
                                <div className="card">
                                    <div className="card-header table-responsive">
                                        <table className="table">
                                            <thead>
                                                <tr>
                                                    <th className="data-serial" scope="col">#</th>
                                                    <th className="data-name" scope="col">Name</th>
                                                    <th className="data-value" scope="col">Marketcap</th>
                                                    <th className="data-price" scope="col">Price</th>
                                                    <th className="data-volume" scope="col">Volume</th>
                                                    <th className="data-supply" scope="col">Circulating Supplly</th>
                                                    <th className="data-change" scope="col">Change (24h)</th>
                                                    <th className="data-graph" scope="col">Price Graph</th>
                                                </tr>
                                            </thead>
                                        </table>
                                    </div>
                                </div>
                                <div className="accordion" id="accordionExample">
                                    <div className="card">
                                        <div className="card-header">
                                                <table className="table table-responsive">
                                                    <tbody>
                                                        <tr>
                                                            <td className="coin-serial" scope="col">01</td>
                                                            <td className="coin-name" scope="col">
                                                                <i className="cc BTC"></i> Bitcoin
                                                        </td>
                                                            <td className="coin-value" scope="col">$130,525,066,827
                                                        </td>
                                                            <td className="coin-price" scope="col">$7,745.91</td>
                                                            <td className="coin-volume" scope="col">$11,747,400,000</td>
                                                            <td className="coin-supply" scope="col">16,850,837 BTC</td>
                                                            <td className="price-change" scope="col">+ 23.86%</td>
                                                            <td className="coin-graph" scope="col">
                                                                <i className="fa pull-right accordion__angle--animated" aria-hidden="true"></i> Price Graph</td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                            
                                        </div>
                                    </div>
                                    <div className="card">
                                        <div className="card-header">
                                                <table className="table table-responsive">
                                                    <tbody>
                                                        <tr>
                                                            <td className="coin-serial" scope="col">02</td>
                                                            <td className="coin-name" scope="col">
                                                                <i className="cc ETH"></i> Ethereum
                                                        </td>
                                                            <td className="coin-value" scope="col">$130,525,066,827
                                                        </td>
                                                            <td className="coin-price" scope="col">$7,745.91</td>
                                                            <td className="coin-volume" scope="col">$11,747,400,000</td>
                                                            <td className="coin-supply" scope="col">16,850,837 BTC</td>
                                                            <td className="price-change" scope="col">+ 23.86%</td>
                                                            <td className="coin-graph" scope="col">
                                                                <i className="fa pull-right accordion__angle--animated" aria-hidden="true"></i> Price Graph</td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                            
                                        </div>
                                    </div>
                                    <div className="card">
                                        <div className="card-header">
                                                <table className="table table-responsive">
                                                    <tbody>
                                                        <tr>
                                                            <td className="coin-serial" scope="col">03</td>
                                                            <td className="coin-name" scope="col">
                                                                <i className="cc XRP"></i> Ripple
                                                        </td>
                                                            <td className="coin-value" scope="col">$130,525,066,827
                                                        </td>
                                                            <td className="coin-price" scope="col">$7,745.91</td>
                                                            <td className="coin-volume" scope="col">$11,747,400,000</td>
                                                            <td className="coin-supply" scope="col">16,850,837 BTC</td>
                                                            <td className="price-change" scope="col">+ 23.86%</td>
                                                            <td className="coin-graph" scope="col">
                                                                <i className="fa pull-right accordion__angle--animated" aria-hidden="true"></i> Price Graph</td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                            
                                        </div>
                                    </div>
                                    <div className="card">
                                        <div className="card-header">
                                                <table className="table table-responsive">
                                                    <tbody>
                                                        <tr>
                                                            <td className="coin-serial" scope="col">04</td>
                                                            <td className="coin-name" scope="col">
                                                                <i className="cc BCH"></i> Bitcoin Cash
                                                        </td>
                                                            <td className="coin-value" scope="col">$130,525,066,827
                                                        </td>
                                                            <td className="coin-price" scope="col">$7,745.91</td>
                                                            <td className="coin-volume" scope="col">$11,747,400,000</td>
                                                            <td className="coin-supply" scope="col">16,850,837 BTC</td>
                                                            <td className="price-change" scope="col">+ 23.86%</td>
                                                            <td className="coin-graph" scope="col">
                                                                <i className="fa pull-right accordion__angle--animated" aria-hidden="true"></i> Price Graph</td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                            
                                        </div>
                                    </div>
                                    <div className="card">
                                        <div className="card-header">
                                                <table className="table table-responsive">
                                                    <tbody>
                                                        <tr>
                                                            <td className="coin-serial" scope="col">05</td>
                                                            <td className="coin-name" scope="col">
                                                                <i className="cc LTC"></i> Litecoin
                                                        </td>
                                                            <td className="coin-value" scope="col">$130,525,066,827
                                                        </td>
                                                            <td className="coin-price" scope="col">$7,745.91</td>
                                                            <td className="coin-volume" scope="col">$11,747,400,000</td>
                                                            <td className="coin-supply" scope="col">16,850,837 BTC</td>
                                                            <td className="price-change" scope="col">+ 23.86%</td>
                                                            <td className="coin-graph" scope="col">
                                                                <i className="fa pull-right accordion__angle--animated" aria-hidden="true"></i> Price Graph</td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                        </div>
                                    </div>
                                    <div className="card">
                                        <div className="card-header">
                                                <table className="table table-responsive">
                                                    <tbody>
                                                        <tr>
                                                            <td className="coin-serial" scope="col">01</td>
                                                            <td className="coin-name" scope="col">
                                                                <i className="cc NEO"></i> NEO
                                                        </td>
                                                            <td className="coin-value" scope="col">$130,525,066,827
                                                        </td>
                                                            <td className="coin-price" scope="col">$7,745.91</td>
                                                            <td className="coin-volume" scope="col">$11,747,400,000</td>
                                                            <td className="coin-supply" scope="col">16,850,837 BTC</td>
                                                            <td className="price-change" scope="col">+ 23.86%</td>
                                                            <td className="coin-graph" scope="col">
                                                                <i className="fa pull-right accordion__angle--animated" aria-hidden="true"></i> Price Graph</td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                            
                                        </div>
                                    </div>
                                    <div className="card">
                                        <div className="card-header">
                                                <table className="table table-responsive">
                                                    <tbody>
                                                        <tr>
                                                            <td className="coin-serial" scope="col">07</td>
                                                            <td className="coin-name" scope="col">
                                                                <i className="cc DASH"></i> Dash
                                                        </td>
                                                            <td className="coin-value" scope="col">$130,525,066,827
                                                        </td>
                                                            <td className="coin-price" scope="col">$7,745.91</td>
                                                            <td className="coin-volume" scope="col">$11,747,400,000</td>
                                                            <td className="coin-supply" scope="col">16,850,837 BTC</td>
                                                            <td className="price-change" scope="col">+ 23.86%</td>
                                                            <td className="coin-graph" scope="col">
                                                                <i className="fa pull-right accordion__angle--animated" aria-hidden="true"></i> Price Graph</td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                        </div>
                                    </div>
                                    <div className="card">
                                        <div className="card-header">
                                                <table className="table table-responsive">
                                                    <tbody>
                                                        <tr>
                                                            <td className="coin-serial" scope="col">08</td>
                                                            <td className="coin-name" scope="col">
                                                                <i className="cc XMR"></i> Monero
                                                        </td>
                                                            <td className="coin-value" scope="col">$130,525,066,827
                                                        </td>
                                                            <td className="coin-price" scope="col">$7,745.91</td>
                                                            <td className="coin-volume" scope="col">$11,747,400,000</td>
                                                            <td className="coin-supply" scope="col">16,850,837 BTC</td>
                                                            <td className="price-change" scope="col">+ 23.86%</td>
                                                            <td className="coin-graph" scope="col">
                                                                <i className="fa pull-right accordion__angle--animated" aria-hidden="true"></i> Price Graph</td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                        </div>
                                    </div>
                                    <div className="card">
                                        <div className="card-header">
                                                <table className="table table-responsive">
                                                    <tbody>
                                                        <tr>
                                                            <td className="coin-serial" scope="col">09</td>
                                                            <td className="coin-name" scope="col">
                                                                <i className="cc ETH-alt"></i> Ethereum classNameic
                                                        </td>
                                                            <td className="coin-value" scope="col">$130,525,066,827
                                                        </td>
                                                            <td className="coin-price" scope="col">$7,745.91</td>
                                                            <td className="coin-volume" scope="col">$11,747,400,000</td>
                                                            <td className="coin-supply" scope="col">16,850,837 BTC</td>
                                                            <td className="price-change" scope="col">+ 23.86%</td>
                                                            <td className="coin-graph" scope="col">
                                                                <i className="fa pull-right accordion__angle--animated" aria-hidden="true"></i> Price Graph</td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                        </div>
                                    </div>
                                    <div className="card">
                                        <div className="card-header">
                                                <table className="table table-responsive">
                                                    <tbody>
                                                        <tr>
                                                            <td className="coin-serial" scope="col">10</td>
                                                            <td className="coin-name" scope="col">
                                                                <i className="cc BCH-alt"></i> Bitcoin Gold
                                                        </td>
                                                            <td className="coin-value" scope="col">$130,525,066,827
                                                        </td>
                                                            <td className="coin-price" scope="col">$7,745.91</td>
                                                            <td className="coin-volume" scope="col">$11,747,400,000</td>
                                                            <td className="coin-supply" scope="col">16,850,837 BTC</td>
                                                            <td className="price-change" scope="col">+ 23.86%</td>
                                                            <td className="coin-graph" scope="col">
                                                                <i className="fa pull-right accordion__angle--animated" aria-hidden="false"></i> Price Graph</td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-lg-6">
                            <p className="m-b-0">Showing 1 to 10 of 1330</p>
                        </div>
                        <div className="col-lg-6">
                            <nav aria-label="Page m-b-0">
                                <ul className="pagination pagination-flat">
                                    <li className="page-item">
                                        <a className="page-link" href="#">Previous</a>
                                    </li>
                                    <li className="page-item">
                                        <a className="page-link active" href="#">1</a>
                                    </li>
                                    <li className="page-item">
                                        <a className="page-link" href="#">2</a>
                                    </li>
                                    <li className="page-item">
                                        <a className="page-link" href="#">3</a>
                                    </li>
                                    <li className="page-item">
                                        <a className="page-link d-none d-sm-block" href="#">...</a>
                                    </li>
                                    <li className="page-item">
                                        <a className="page-link" href="#">188</a>
                                    </li>
                                    <li className="page-item">
                                        <a className="page-link" href="#">Next</a>
                                    </li>
                                </ul>
                            </nav>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
