import React, { useRef, useEffect } from 'react';
import {isMobile} from 'react-device-detect';

const { tableau } = window;

function MainDashboard() {
    const ref = useRef(null);
    const url = 'https://public.tableau.com/views/Bancor3PublicDashboard/Bancor3Dashboard';
    let device = 'desktop';
    if(isMobile) {
        device = 'phone';
    }

    const options = {
        hideToolbar: true,
        hideTabs: true,
        device: device,
        onFirstInteractive: function () {
            console.log("Loaded Main Dashboard.");
        },
    };

    const initViz = () => {
        // Dispose of previous Vizzes
        let viz = window.tableau.VizManager.getVizs()[0];
        if (viz) {
            viz.dispose();
        }

        viz = new tableau.Viz(ref.current, url, options);
    };

    useEffect(initViz, []);

    return (
        <div ref={ref} />
    );
};

export default MainDashboard;