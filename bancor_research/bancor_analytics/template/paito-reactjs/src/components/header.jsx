import React from 'react';
import logoImg from "../assets/images/logo-mini.png";
import userImg from "../assets/images/user.png";
import { Dropdown } from "react-bootstrap";
import { Link } from "react-router-dom";

export default function Header(props) {
    const { show, showToggle } = props;
    return (
        <div className="header fixed-top">
            <div className="nav-header">
                <div className="brand-logo">
                    <Link to="/">
                        <img src={logoImg} alt="logo" />
                        <span className="brand-title pl-3">Paito</span>
                    </Link>
                </div>
            </div>

            <div className="header-content">
                <div className="header-left d-flex">
                    <div className="nav-control">
                        <div className={show ? "hamburger is-active" : "hamburger"} onClick={showToggle}>
                            <span className="line"></span>
                            <span className="line"></span>
                            <span className="line"></span>
                        </div>
                    </div>
                    <div className="nav-search-box">
                        <i className="fa fa-search"></i>
                        <input type="search" placeholder="Search" />
                    </div>
                </div>
            </div>

            <div className="navbar-custom-menu pull-right d-flex nav-right">
                <Dropdown as="div">
                    <Dropdown.Toggle as="div">
                        <a className="dropdown-toggle" href="#">
                            <span className="badge badge-danger">
                                <span></span>
                            </span>
                            <i className="fa fa-envelope"></i>
                        </a>
                    </Dropdown.Toggle>
                    <Dropdown.Menu className="dropdown-menu-right inbox-dropdown">
                        
                            <div className="message-options">
                                <a href="#" className="single-message">Message</a>
                                <a href="#" className="view-all-message pull-right">View All</a>
                                <a href="#" className="compose-message pull-right">Compose</a>
                            </div>
                            <a className="dropdown-item" href="#">
                                <div className="media">
                                    <img className="mr-3" src={userImg} alt="Generic placeholder image" />
                                    <div className="media-body">
                                        <h6 className="mt-0">
                                            John Doe
                                        <span className="time">March 21, 2018</span>
                                        </h6>
                            It is a long established fact that a reader...
                        </div>
                                </div>
                            </a>
                            <a className="dropdown-item" href="#">
                                <div className="media">
                                    <img className="mr-3" src={userImg} alt="Generic placeholder image" />
                                    <div className="media-body">
                                        <h6 className="mt-0">
                                            John Doe
                                        <span className="time">March 21, 2018</span>
                                        </h6>
                            It is a long established fact that a reader...
                        </div>
                                </div>
                            </a>
                            <a className="dropdown-item" href="#">
                                <div className="media">
                                    <img className="mr-3" src={userImg} alt="Generic placeholder image" />
                                    <div className="media-body">
                                        <h6 className="mt-0">
                                            John Doe
                                        <span className="time">March 21, 2018</span>
                                        </h6>
                            It is a long established fact that a reader...
                        </div>
                                </div>
                            </a>
                            <a className="dropdown-item" href="#">
                                <div className="media">
                                    <img className="mr-3" src={userImg} alt="Generic placeholder image" />
                                    <div className="media-body">
                                        <h6 className="mt-0">
                                            John Doe
                                        <span className="time">March 21, 2018</span>
                                        </h6>
                            It is a long established fact that a reader...
                        </div>
                                </div>
                            </a>
                            <a className="dropdown-item" href="#">
                                <div className="media">
                                    <img className="mr-3" src={userImg} alt="Generic placeholder image" />
                                    <div className="media-body">
                                        <h6 className="mt-0">
                                            John Doe
                                       <span className="time">March 21, 2018</span>
                                        </h6>
                            It is a long established fact that a reader...
                        </div>
                                </div>
                            </a>
                        
                    </Dropdown.Menu>
                </Dropdown>
                <Dropdown as="div">
                    <Dropdown.Toggle as="div">
                        <a className="dropdown-toggle" href="#">
                            <span className="badge badge-danger">
                                <span></span>
                            </span>
                            <i className="fa fa-bell"></i>
                        </a>
                    </Dropdown.Toggle>
                    <Dropdown.Menu className="dropdown-menu-right notification-dropdown">
                        <li className="header">You have 10 notifications</li>
                        <li>
                            <ul className="menu">
                                <li>
                                    <a href="#"> <i className="fa fa-users text-aqua"></i> 5 new members joined today </a>
                                </li>
                                <li>
                                    <a href="#"> <i className="fa fa-warning text-yellow"></i> Very long description here that may not fit into the page and may cause design problems </a>
                                </li>
                                <li>
                                    <a href="#"> <i className="fa fa-users text-red"></i> 5 new members joined </a>
                                </li>
                                <li>
                                    <a href="#"> <i className="fa fa-shopping-cart text-green"></i> 25 sales made </a>
                                </li>
                                <li>
                                    <a href="#"> <i className="fa fa-user text-red"></i> You changed your username </a>
                                </li>
                            </ul>
                        </li>
                        <li className="footer">
                            <a href="#">View all</a>
                        </li>
                    </Dropdown.Menu>
                </Dropdown>
                <Dropdown as="div"> 
                <Dropdown.Toggle as="div">
                    <a className="dropdown-toggle" href="#" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        <i className="fa fa-cog"></i>
                    </a>
                    </Dropdown.Toggle>
                    <Dropdown.Menu className="dropdown-menu-right"> 
                        <a className="dropdown-item" href="#">Action</a>
                        <a className="dropdown-item" href="#">Another action</a>
                        <a className="dropdown-item" href="#">Something else</a>
                    </Dropdown.Menu>
                </Dropdown>
                <Dropdown as="div"> 
                    <Dropdown.Toggle as="div" className="user-profile-dropdown">
                    <a className="dropdown-toggle user-profile-dropdown" href="#" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        <span className="user-img">
                            <img src={userImg} alt="user" />
                        </span>
                        <span className="user-name">John Doe</span>
                    </a>
                    </Dropdown.Toggle>
                    <Dropdown.Menu  className="dropdown-menu dropdown-menu-right"> 
                        <a className="dropdown-item" href="#">
                            <i className="fa fa-user-circle" aria-hidden="true"></i> Profile 
                        </a>
                        <a className="dropdown-item" href="#"> 
                            <i className="fa fa-cog"></i> Setting 
                        </a>
                        <a className="dropdown-item" href="#"> 
                            <i className="fa fa-question-circle" aria-hidden="true"></i> Help
                       </a>
                        <a className="dropdown-item" href="#"> 
                            <i className="fa fa-power-off" aria-hidden="true"></i> Logout 
                        </a>
                    </Dropdown.Menu>
                </Dropdown>
            </div>
        </div>

    )
}
