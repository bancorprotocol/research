import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardBody, Col } from 'reactstrap';

const NumerousList = () => {
  const { t } = useTranslation('common');

  return (
    <Col md={12} lg={6}>
      <Card>
        <CardBody>
          <div className="card__title">
            <h5 className="bold-text">{t('ui_elements.typography.numerous_list')}</h5>
            <h5 className="subhead">Use default <span className="red-text">ol</span></h5>
          </div>
          <ol className="list">
            <li><p>Nulla tellus elit, varius non commodo eget</p></li>
            <li><p>Cum sociis natoque penatibus</p></li>
            <li><p>Curabitur bibendum ornare dolor</p></li>
          </ol>
        </CardBody>
      </Card>
    </Col>
  );
};

export default NumerousList;
