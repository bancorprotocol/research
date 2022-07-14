import React from 'react';
import { NavLink } from 'react-router-dom'
import MetisMenu from '@metismenu/react';
import SimpleBar from 'simplebar-react';
import 'metismenujs/dist/metismenujs.css';
import "../../node_modules/simplebar-react/dist/simplebar.min.css";
export default function Sidenav(props) {
    const sidebarHeight = window.innerHeight;
    return (
        <>
        <div className="nk-sidebar">
            <div className="nk-nav-scroll">
             <SimpleBar style={{ maxHeight: sidebarHeight }}>
                <MetisMenu className="metismenu" id="menu">
                    <li className="pt-3">
                        <NavLink to="/" exact={true}>
                            <i className="fa fa-dashboard"></i>
                            <span className="nav-text">Dashboard</span>
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/trading" activeClassName="active">
                            <i className="fa fa-line-chart"></i>
                            <span className="nav-text">Trading</span>
                        </NavLink>
                    </li>

                    <li>
                        <NavLink to="/marketcap">
                            <i className="fa fa-bolt"></i>
                            <span className="nav-text">Marketcap</span>
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/ico">
                            <i className="fa fa-btc"></i>
                            <span className="nav-text">ICO</span>
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/buy_sell">
                            <i className="fa fa-usd"></i>
                            <span className="nav-text">Buy and Sell</span>
                        </NavLink>
                    </li>
                    <li>
                    <NavLink to="/wallet">
                        <i className="fa fa-credit-card"></i>
                        <span className="nav-text">My Wallet</span>
                    </NavLink>
                    </li>
                    <li>
                    <NavLink to="/currency_exchange">
                        <i className="fa fa-refresh"></i>
                        <span className="nav-text">Currency Exchange</span>
                    </NavLink>
                    </li>
                    <li>
                        <a className="has-arrow" href="#" aria-expanded="false">
                            <i className="fa fa-folder-open"></i>
                            <span className="nav-text">UI Elements</span>
                        </a>
                        <ul aria-expanded="false">
                            <li>
                                <NavLink to="/grids">
                                  <span className="nav-text-2">Grids</span>
                                </NavLink>
                            </li>
                            <li>
                                <NavLink to="/buttons">
                                    <span className="nav-text-2">Buttons</span>
                                </NavLink>
                            </li>
                            <li>
                                <NavLink to="/tables">
                                    <span className="nav-text-2">Tables</span>  
                                </NavLink>
                            </li>
                            <li>
                               <NavLink to="/tabs">
                                  <span className="nav-text-2">Tabs</span>  
                                </NavLink>
                            </li>
                            <li>
                                <NavLink to="/forms">
                                    <span className="nav-text-2">Forms</span>  
                                </NavLink>
                            </li>
                            <li>
                                <NavLink to="/charts">
                                    <span className="nav-text-2">Charts</span>
                                </NavLink>
                            </li>
                            <li>
                                <NavLink to="/pagination">
                                    <span className="nav-text-2">Pagination</span>
                                </NavLink>
                            </li>
                        </ul>
                    </li>
                    <li>
                        <NavLink to="/register">
                            <i className="fa fa-key"></i>
                            <span className="nav-text">Register</span>
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/login">
                            <i className="fa fa-user"></i>
                            <span className="nav-text">Login</span>
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/recover_password">
                            <i className="fa fa-lock"></i>
                            <span className="nav-text">Recover Password</span>
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="reset_password">
                            <i className="fa fa-lock"></i>
                            <span className="nav-text">Reset Password</span>
                        </NavLink>
                    </li>

                    <li>
                        <NavLink to="/faq">
                            <i className="fa fa-question-circle"></i>
                            <span className="nav-text">FAQ</span>
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="error">
                            <i className="fa fa-exclamation-circle"></i>
                            <span className="nav-text">Error</span>
                        </NavLink>
                    </li>
                  </MetisMenu>
                 </SimpleBar>
            </div>
        </div>
        </>
    )
}
