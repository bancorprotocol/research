import React, {useState} from 'react';
import { Tab, Nav } from "react-bootstrap";

export default function TabsFour() {
    const [currentEvent, setCurrentEvent] = useState("tab_01");
    return (
        <div className="card tab-container">
            <Tab.Container defaultActiveKey="tab_01" onSelect={(key) => setCurrentEvent(key)}>
                <div className="card-body tab-left">
                    <h4 className="card-title">Vertical Nav Pill</h4>
                    <div className="row m-t-30">
                        <div className="col-xl-4">
                            <div className="nav flex-column nav-pills tab-head">
                                <Nav.Link eventKey="tab_01" className={currentEvent === "tab_01" ? "active" : "nav-link-2"}>Tab A</Nav.Link>
                                <Nav.Link eventKey="tab_02" className={currentEvent === "tab_02" ? "active" : "nav-link-2"}>Tab B</Nav.Link>
                                <Nav.Link eventKey="tab_03" className={currentEvent === "tab_03" ? "active" : "nav-link-2"}>Tab C</Nav.Link>
                                <Nav.Link eventKey="tab_04" className={currentEvent === "tab_04" ? "active" : "nav-link-2"}>Tab D</Nav.Link>
                            </div>
                        </div>
                        <div className="col-xl-8">
                            <div className="tab-content">
                                <Tab.Pane eventKey="tab_01">
                                    <p>
                                        Cillum ad ut irure tempor velit nostrud occaecat ullamco aliqua anim Lorem sint. Veniam sint duis incididunt do esse magna mollit excepteur laborum qui. Id id reprehenderit sit est eu aliqua occaecat quis
                                        et velit excepteur laborum mollit dolore eiusmod. Ipsum dolor in occaecat commodo et voluptate minim reprehenderit mollit pariatur. Deserunt non laborum enim et cillum eu deserunt excepteur ea incididunt
                                        minim occaecat.
                                    </p>
                                </Tab.Pane>
                                <Tab.Pane eventKey="tab_02">
                                    <p>
                                        Cillum ad ut irure tempor velit nostrud occaecat ullamco aliqua anim Lorem sint. Veniam sint duis incididunt do esse magna mollit excepteur laborum qui. Id id reprehenderit sit est eu aliqua occaecat quis
                                        et velit excepteur laborum mollit dolore eiusmod. Ipsum dolor in occaecat commodo et voluptate minim reprehenderit mollit pariatur. Deserunt non laborum enim et cillum eu deserunt excepteur ea incididunt
                                        minim occaecat.
                                    </p>
                                </Tab.Pane>
                                <Tab.Pane eventKey="tab_03">
                                    <p>
                                        Cillum ad ut irure tempor velit nostrud occaecat ullamco aliqua anim Lorem sint. Veniam sint duis incididunt do esse magna mollit excepteur laborum qui. Id id reprehenderit sit est eu aliqua occaecat quis
                                        et velit excepteur laborum mollit dolore eiusmod. Ipsum dolor in occaecat commodo et voluptate minim reprehenderit mollit pariatur. Deserunt non laborum enim et cillum eu deserunt excepteur ea incididunt
                                        minim occaecat.
                                    </p>
                                </Tab.Pane>
                                <Tab.Pane eventKey="tab_04">
                                    <p>
                                        Cillum ad ut irure tempor velit nostrud occaecat ullamco aliqua anim Lorem sint. Veniam sint duis incididunt do esse magna mollit excepteur laborum qui. Id id reprehenderit sit est eu aliqua occaecat quis
                                        et velit excepteur laborum mollit dolore eiusmod. Ipsum dolor in occaecat commodo et voluptate minim reprehenderit mollit pariatur. Deserunt non laborum enim et cillum eu deserunt excepteur ea incididunt
                                        minim occaecat.
                                    </p>
                                </Tab.Pane>
                            </div>
                        </div>
                    </div>
                </div>
            </Tab.Container>
        </div>
    )
}
