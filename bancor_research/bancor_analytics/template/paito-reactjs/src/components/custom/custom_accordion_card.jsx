import React, {useContext} from 'react';
import { Accordion, Card } from "react-bootstrap";
import { useAccordionToggle, AccordionContext } from 'react-bootstrap';

export default function CustomAccordionCard(props) {
    const { title, eventKey, className } = props;
    const CustomToggle = () => {
        const decoratedOnClick = useAccordionToggle(eventKey, () => { });
        const currentEventKey = useContext(AccordionContext);
        const isCurrentEventKey = currentEventKey === eventKey;
        const icon = isCurrentEventKey ? <i className="fa fa-angle-up pull-right "></i>
            : <i className="fa fa-angle-down pull-right "></i>;

        return (
            <h4 onClick={decoratedOnClick}>
                {title}
                {icon}
            </h4>
        );
    }

    return (
        <Card>
            <Card.Header>
                <Accordion.Toggle as="div" variant="link" eventKey={eventKey}>
                    <CustomToggle eventKey={eventKey}>
                        {title}
                    </CustomToggle>
                </Accordion.Toggle>
            </Card.Header>
            <Accordion.Collapse eventKey={eventKey}>
                <Card.Body>
                    {props.children}
                </Card.Body>
            </Accordion.Collapse>
        </Card>
    )
}
