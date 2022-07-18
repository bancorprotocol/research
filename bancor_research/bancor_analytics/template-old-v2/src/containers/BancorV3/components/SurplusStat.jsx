import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardBody, Col } from 'reactstrap';
import {
  BarChart, Bar, Cell, ResponsiveContainer,
} from 'recharts';
import TrendingUpIcon from 'mdi-react/TrendingUpIcon';

const SurplusStat = () => {
  const { t } = useTranslation('common');
  const [activeIndex, setActiveIndex] = useState(0);

  return (
    <Col md={12} xl={3} lg={6} xs={12}>
      <Card>
        <CardBody className="dashboard__card-widget">
          <div className="card__title">
            <h5 className="bold-text">Surplus / Deficit</h5>
          </div>
          <div className="dashboard__total">
            {/* <TrendingDownIcon className="dashboard__trend-icon" /> */}
            <p className="plyr__video-embed">
              {/* eslint-disable-next-line max-len */}
              <iframe src="https://public.tableau.com/views/UI-test/SurplusStat?:showVizHome=no&:embed=true&:toolbar=no" width="100%" frameBorder="0" scrolling="yes" title="test" />
            </p>
          </div>
        </CardBody>
      </Card>
    </Col>
  );
};

export default SurplusStat;
