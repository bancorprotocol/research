import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  Card, CardBody, Col, Progress,
} from 'reactstrap';

const MultisizedProgressBars = () => {
  const { t } = useTranslation('common');

  return (
    <Col md={12} lg={6}>
      <Card>
        <CardBody>
          <div className="card__title">
            <h5 className="bold-text">{t('ui_elements.progress_bars.multisized_progress_bars')}</h5>
            <h5 className="subhead">Use default progress with class
              <span className="red-text"> progress-wrap--small</span>,
              <span className="red-text"> progress-wrap--middle</span>,
              <span className="red-text"> progress-wrap--big</span>
            </h5>
          </div>
          <div className="progress-wrap">
            <Progress value={20} />
          </div>
          <div className="progress-wrap progress-wrap--small">
            <Progress value={40} />
          </div>
          <div className="progress-wrap progress-wrap--middle">
            <Progress value={60} />
          </div>
          <div className="progress-wrap progress-wrap--big">
            <Progress value={80} />
          </div>
        </CardBody>
      </Card>
    </Col>
  );
};

export default MultisizedProgressBars;
