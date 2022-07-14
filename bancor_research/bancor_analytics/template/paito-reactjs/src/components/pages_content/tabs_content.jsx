import React from 'react';
import TabsOne from "../custom/tabs_one";
import TabsTwo from "../custom/tabs_two";
import TabsThree from "../custom/tabs_three";
import TabsFour from "../custom/tabs_four";
export default function TabsContent() {
    
    return (
        <div className="content-body">
            <div className="container-fluid">
                <div className="row">
                    <div className="col-lg-12">
                        <h2 className="page-title">Tabs</h2>
                    </div>
                </div>
            </div>
            <div className="tabs-section">
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-lg-6">
                            <TabsOne/>
                        </div>
                        <div className="col-lg-6">
                            <TabsTwo/>
                        </div>
                        <div className="col-lg-6">
                            <TabsThree/>
                        </div>
                        <div className="col-lg-6">
                            <TabsFour/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
