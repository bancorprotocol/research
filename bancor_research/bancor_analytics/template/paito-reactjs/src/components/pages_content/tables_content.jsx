import React from 'react';
export default function TablesContent() {
    return (
        <div className="content-body">
            <div className="container-fluid">
                <div className="row">
                    <div className="col-lg-12">
                        <h2 className="page-title">Table</h2>
                    </div>
                </div>
            </div>
            <div className="tables-section">
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-lg-4">
                            <div className="table-data">
                                <div className="card rounded-0">
                                    <div className="card-header">
                                        <h4 className="mb-0">
                                            Marketcap
                                        </h4>
                                    </div>
                                    <div id="table-one" className="table-responsive">
                                        <table className="table m-b-0">
                                            <thead>
                                                    <tr className="search-block">
                                                        <th scope="col">Show 15</th>
                                                        <th colspan="2" scope="col">
                                                            <span>Search</span>
                                                            <input placeholder="Search" type="search"/>
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
                                                    <tr>
                                                        <td>XMR</td>
                                                        <td>$12,623.40</td>
                                                        <td className="change">
                                                            <i className="fa fa-angle-up"></i>
                                                            <span>+6.50%</span>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td>ADA</td>
                                                        <td>$12,623.40</td>
                                                        <td className="change">
                                                            <i className="fa fa-angle-up"></i>
                                                            <span>+6.50%</span>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td>EOS</td>
                                                        <td>$12,623.40</td>
                                                        <td className="change">
                                                            <i className="fa fa-angle-up"></i>
                                                            <span>+6.50%</span>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                    </table>
                                </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-lg-8">
                                <div className="accordion table-data">
                                    <div className="card rounded-0">
                                        <div className="card-header">
                                            <h4 className="mb-0">
                                                Recent Trading Activities
                                            </h4>
                                        </div>
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
                                    </div>
                                </div>
                            </div>
                            <div className="col-lg-6">
                                <div className="accordion table-data">
                                    <div className="card rounded-0">
                                        <div className="card-header">
                                            <h4 className="mb-0">
                                                Recent Buying Cryptocurrencies
                                            </h4>
                                        </div>
                                        <div id="table-three" className="collapse show table-responsive">
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
                                    </div>
                                </div>
                            </div>
                            <div className="col-lg-6">
                                <div className="accordion table-data">
                                    <div className="card rounded-0">
                                        <div className="card-header">
                                            <h4 className="mb-0">
                                                Recent Selling Orders
                                            </h4>
                                        </div>
                                        <div id="table-four" className="table-responsive">
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
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
    )
}
