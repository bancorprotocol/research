import React from 'react';
import Header from "../components/header";
import Sidenav from "../components/sidenav";
import Footer from "../components/footer";
import useToggleShow from "../hooks/use_toggle_show";

export default function PageLayout(props) {
    const [show, showToggle] = useToggleShow();
    return (
       <>
        <div className={show ? "App nav-mini" : "App"}>
            <Header
                show={show}
                showToggle={showToggle}
            />
            <Sidenav />
            {props.children}
            <Footer/>
        </div>
      </>
    )
}
