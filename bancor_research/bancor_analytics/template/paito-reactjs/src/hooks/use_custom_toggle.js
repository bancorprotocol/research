import React, {useState} from 'react';
import { useAccordionToggle } from "react-bootstrap";

export default function useCustomToggle() {
    const [eventKeyName, setEventKeyName] = useState("null");
  const  CustomToggle =({ children, eventKey })=> {
        const decoratedOnClick = useAccordionToggle(eventKey, () =>
            setEventKeyName(eventKey)
        );

      <button
          type="button"
          style={{ backgroundColor: 'pink' }}
          onClick={decoratedOnClick}
      >
          {children}
      </button>
  }

    return [eventKeyName, CustomToggle];
}
