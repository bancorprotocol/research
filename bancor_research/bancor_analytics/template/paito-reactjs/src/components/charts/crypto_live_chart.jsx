import React, {useState,useEffect} from 'react';
import { Helmet } from "react-helmet";
import { useLocation } from "react-router-dom";
export default function CryptoLiveChart() {
    const location = useLocation();
    const [embededScript,setEmbededScript] = useState();
    useEffect(() => {
        setEmbededScript(embedScript);
    }, [location]);

    const embedScript = () => {
        const baseUrl = "https://widgets.cryptocompare.com/";
        let appName = encodeURIComponent(window.location.hostname) || "local";
        var s = document.createElement("script");
        s.type = "text/javascript";
        s.async = true;
        var theUrl = baseUrl + 'serve/v3/coin/chart?fsym=BTC&tsyms=USD,EUR,CNY,GBP';
        s.src = theUrl + (theUrl.indexOf("?") >= 0 ? "&" : "?") + "app=" + appName;
        var getId = document.getElementById("trading-live");
        getId.append(s);
    }
    return (
       <>
            <div className="row">
                <div className="col-lg-12">
                    <h2 className="page-title">Trading</h2>
                </div>
            </div>
            <div className="row">
                <div className="col-xl-12">
                    <div className="card m-b-30">
                        <div className="card-body">
                            <div className="trading-view">
                                <div id="trading-live">
                                    <Helmet>
                                        {embededScript}
                                    </Helmet>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
       </>
    )
}
