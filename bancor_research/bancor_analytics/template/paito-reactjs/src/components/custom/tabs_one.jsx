import React,{useState} from 'react';
import { Nav, Tab } from "react-bootstrap";

export default function TabsOne() {
    const [currentEvent, setCurrentEvent] = useState("tab_01");
    return (
        <Tab.Container id="left-tabs-example" defaultActiveKey="tab_01" onSelect={(key) => setCurrentEvent(key)}>
            <div className="card tab-container">
                <div className="card-body borderd-tabs">
                    <h4 className="card-title">Tabs Style One</h4>
                    <ul className="nav nav-pills m-t-30 m-b-30">
                        <li className="nav-item">
                            <Nav.Link eventKey="tab_01" className={currentEvent === "tab_01" ? "active" : "nav-link-2"}>Tab 1</Nav.Link>
                        </li>
                        <li className="nav-item">
                            <Nav.Link eventKey="tab_02" className={currentEvent === "tab_02" ? "active" : "nav-link-2"}>Tab 2</Nav.Link>
                        </li>
                        <li className="nav-item">
                            <Nav.Link eventKey="tab_03" className={currentEvent === "tab_03" ? "active" : "nav-link-2"}>Tab 3</Nav.Link>
                        </li>
                        <li className="nav-item">
                            <Nav.Link eventKey="tab_04" className={currentEvent === "tab_04" ? "active" : "nav-link-2"}>Tab 4</Nav.Link>
                        </li>
                    </ul>
                    <Tab.Content>
                        <div className="tab-content br-n pn">
                            <Tab.Pane eventKey="tab_01">
                                <p>
                                    Tab One, consectetur adipisicing elit. Magnam, ea temporibus unde labore, laudantium obcaecati cupiditate tempore inventore iusto distinctio accusamus. Quos laborum adipisci, eum possimus pariatur dolor, odio? Iste facilis neque, tenetur, nemo soluta, cum fugit similique, modi maiores consectetur corporis incidunt quo asperiores. Nesciunt perferendis maiores ipsa numquam, obcaecati eaque quas. Eligendi autem, vero corrupti totam eveniet. Repellendus adipisci eos laborum assumenda incidunt dolore alias, nulla illo. Tempore omnis, perspiciatis illo soluta, sunt fugiat repudiandae quod voluptate doloremque, assumenda dolores nulla sequi ipsam quia culpa ducimus vero quasi. Praesentium quo quis, maxime maiores vero, vitae consectetur! Quaerat, sed!
                                </p>
                            </Tab.Pane>
                            <Tab.Pane eventKey="tab_02">
                                <p>
                                    Tab Two sit amet, consectetur adipisicing elit. Magnam, ea temporibus unde labore, laudantium obcaecati cupiditate tempore inventore iusto distinctio accusamus. Quos laborum adipisci, eum possimus pariatur dolor, odio? Iste facilis neque, tenetur, nemo soluta, cum fugit similique, modi maiores consectetur corporis incidunt quo asperiores. Nesciunt perferendis maiores ipsa numquam, obcaecati eaque quas. Eligendi autem, vero corrupti totam eveniet. Repellendus adipisci eos laborum assumenda incidunt dolore alias, nulla illo. Tempore omnis, perspiciatis illo soluta, sunt fugiat repudiandae quod voluptate doloremque, assumenda dolores nulla sequi ipsam quia culpa ducimus vero quasi. Praesentium quo quis, maxime maiores vero, vitae consectetur! Quaerat, sed!
                                </p>
                            </Tab.Pane>
                            <Tab.Pane eventKey="tab_03">
                                <p>
                                    Tab Three dolor sit amet, consectetur adipisicing elit. Magnam, ea temporibus unde labore, laudantium obcaecati cupiditate tempore inventore iusto distinctio accusamus. Quos laborum adipisci, eum possimus pariatur dolor, odio? Iste facilis neque, tenetur, nemo soluta, cum fugit similique, modi maiores consectetur corporis incidunt quo asperiores. Nesciunt perferendis maiores ipsa numquam, obcaecati eaque quas. Eligendi autem, vero corrupti totam eveniet. Repellendus adipisci eos laborum assumenda incidunt dolore alias, nulla illo. Tempore omnis, perspiciatis illo soluta, sunt fugiat repudiandae quod voluptate doloremque, assumenda dolores nulla sequi ipsam quia culpa ducimus vero quasi. Praesentium quo quis, maxime maiores vero, vitae consectetur! Quaerat, sed!
                                </p>
                            </Tab.Pane>
                            <Tab.Pane eventKey="tab_04">
                                <p>
                                    Tab Three sit amet, consectetur adipisicing elit. Magnam, ea temporibus unde labore, laudantium obcaecati cupiditate tempore inventore iusto distinctio accusamus. Quos laborum adipisci, eum possimus pariatur dolor, odio? Iste facilis neque, tenetur, nemo soluta, cum fugit similique, modi maiores consectetur corporis incidunt quo asperiores. Nesciunt perferendis maiores ipsa numquam, obcaecati eaque quas. Eligendi autem, vero corrupti totam eveniet. Repellendus adipisci eos laborum assumenda incidunt dolore alias, nulla illo. Tempore omnis, perspiciatis illo soluta, sunt fugiat repudiandae quod voluptate doloremque, assumenda dolores nulla sequi ipsam quia culpa ducimus vero quasi. Praesentium quo quis, maxime maiores vero, vitae consectetur! Quaerat, sed!
                                </p>
                            </Tab.Pane>
                        </div>
                    </Tab.Content>
                </div>
            </div>
        </Tab.Container>
    )
}
