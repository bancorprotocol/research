import React from 'react';
import { Accordion } from "react-bootstrap";
import CustomAccordionCard from "../custom/custom_accordion_card";
export default function FaqContent() {

    return (
        <div className="content-body">
            <div className="container-fluid">
                <div className="row">
                    <div className="col-lg-12">
                        <h2 className="page-title">FAQ</h2>
                    </div>
                </div>
            </div>

            <div className="faq-section mb-5">
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-lg-12">
                            <Accordion
                                defaultActiveKey="question_1"
                                className="faq-accordion"
                            >
                                <CustomAccordionCard
                                  eventKey="question_1"
                                    title="Aliquam non lacus ornare, egestas lectus"
                                >
                                <div className="qs-answer px-3">
                                        <p>Lorem ipsum, dolor sit amet consectetur adipisicing elit. Labore, repudiandae voluptatibus quo necessitatibus obcaecati ad nisi dolore deleniti aspernatur, dolor voluptates facilis consequatur exercitationem adipisci laudantium possimus. Eligendi, vero corporis.</p>
                                        <p>Lorem ipsum dolor sit, amet consectetur adipisicing elit. Laboriosam voluptas saepe ipsam debitis maiores quaerat ab nostrum, similique obcaecati et impedit doloribus molestiae enim perspiciatis!</p>
                                </div>
                                </CustomAccordionCard>
                                <CustomAccordionCard
                                  eventKey="question_2"
                                   title="Aliquam non lacus ornare, egestas lectus at, vulputate augue"
                                >
                                    <div className="qs-answer px-3">
                                        <p>Lorem ipsum, dolor sit amet consectetur adipisicing elit. Labore, repudiandae voluptatibus quo necessitatibus obcaecati ad nisi dolore deleniti aspernatur, dolor voluptates facilis consequatur exercitationem adipisci laudantium possimus. Eligendi, vero corporis.</p>
                                        <p>Lorem ipsum dolor sit, amet consectetur adipisicing elit. Laboriosam voluptas saepe ipsam debitis maiores quaerat ab nostrum, similique obcaecati et impedit doloribus molestiae enim perspiciatis!</p>
                                    </div>
                                </CustomAccordionCard>
                                <CustomAccordionCard
                                  eventKey="question_3"
                                   title="Aliquam non lacus ornare, egestas lectus at, vulputate augue"
                                >
                                    <div className="qs-answer px-3">
                                        <p>Lorem ipsum, dolor sit amet consectetur adipisicing elit. Labore, repudiandae voluptatibus quo necessitatibus obcaecati ad nisi dolore deleniti aspernatur, dolor voluptates facilis consequatur exercitationem adipisci laudantium possimus. Eligendi, vero corporis.</p>
                                        <p>Lorem ipsum dolor sit, amet consectetur adipisicing elit. Laboriosam voluptas saepe ipsam debitis maiores quaerat ab nostrum, similique obcaecati et impedit doloribus molestiae enim perspiciatis!</p>
                                    </div>
                                </CustomAccordionCard>
                                <CustomAccordionCard
                                  eventKey="question_4"
                                   title="Aliquam non lacus ornare, egestas lectus at, vulputate augue"
                                >
                                    <div className="qs-answer px-3">
                                        <p>Lorem ipsum, dolor sit amet consectetur adipisicing elit. Labore, repudiandae voluptatibus quo necessitatibus obcaecati ad nisi dolore deleniti aspernatur, dolor voluptates facilis consequatur exercitationem adipisci laudantium possimus. Eligendi, vero corporis.</p>
                                        <p>Lorem ipsum dolor sit, amet consectetur adipisicing elit. Laboriosam voluptas saepe ipsam debitis maiores quaerat ab nostrum, similique obcaecati et impedit doloribus molestiae enim perspiciatis!</p>
                                    </div>
                                </CustomAccordionCard>
                                <CustomAccordionCard
                                  eventKey="question_5"
                                   title="Aliquam non lacus ornare, egestas lectus at, vulputate augue"
                                >
                                    <div className="qs-answer px-3">
                                        <p>Lorem ipsum, dolor sit amet consectetur adipisicing elit. Labore, repudiandae voluptatibus quo necessitatibus obcaecati ad nisi dolore deleniti aspernatur, dolor voluptates facilis consequatur exercitationem adipisci laudantium possimus. Eligendi, vero corporis.</p>
                                        <p>Lorem ipsum dolor sit, amet consectetur adipisicing elit. Laboriosam voluptas saepe ipsam debitis maiores quaerat ab nostrum, similique obcaecati et impedit doloribus molestiae enim perspiciatis!</p>
                                    </div>
                                </CustomAccordionCard>
                                <CustomAccordionCard
                                  eventKey="question_6"
                                   title="Aliquam non lacus ornare, egestas lectus at, vulputate augue"
                                >
                                    <div className="qs-answer px-3">
                                        <p>Lorem ipsum, dolor sit amet consectetur adipisicing elit. Labore, repudiandae voluptatibus quo necessitatibus obcaecati ad nisi dolore deleniti aspernatur, dolor voluptates facilis consequatur exercitationem adipisci laudantium possimus. Eligendi, vero corporis.</p>
                                        <p>Lorem ipsum dolor sit, amet consectetur adipisicing elit. Laboriosam voluptas saepe ipsam debitis maiores quaerat ab nostrum, similique obcaecati et impedit doloribus molestiae enim perspiciatis!</p>
                                    </div>
                                </CustomAccordionCard>
                            </Accordion>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
