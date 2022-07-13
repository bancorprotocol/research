import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardBody, Col } from 'reactstrap';

const Highlight = () => {
  const { t } = useTranslation('common');

  return (
    <Col md={12} lg={6}>
      <Card>
        <CardBody>
          <div className="card__title">
            <h5 className="bold-text">{t('ui_elements.typography.highlight')}</h5>
            <h5 className="subhead">Use span with class <span className="red-text">highlight</span></h5>
          </div>
          <p className="typography-message">
            Nulla tellus elit, varius non <span className="highlight">commodo</span> eget, mattis vel eros.
            In sed ornare nulla. Nullam quis risuseget urna mollis ornare vel eu leo. Cum sociis natoque
            penatibus et magnis dis parturient montes,nascetur ridiculus mus.
          </p>
        </CardBody>
      </Card>
    </Col>
  );
};

export default Highlight;
