import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardBody, Col } from 'reactstrap';
import {
  HorizontalGridLines,
  VerticalBarSeries,
  VerticalGridLines,
  XAxis,
  FlexibleWidthXYPlot,
  YAxis,
} from 'react-vis';

const Bar = () => {
  const { t } = useTranslation('common');

  return (
    <Col xs={12} md={12} lg={12} xl={4}>
      <Card>
        <CardBody>
          <div className="card__title">
            <h5 className="bold-text">{t('charts.react_vis.bars')}</h5>
          </div>
          <div className="react-vis" dir="ltr">
            <FlexibleWidthXYPlot
              xType="ordinal"
              height={250}
              xDistance={100}
            >
              <VerticalGridLines />
              <HorizontalGridLines />
              <XAxis />
              <YAxis />
              <VerticalBarSeries
                data={[
                  { x: 'A', y: 10 },
                  { x: 'B', y: 5 },
                  { x: 'C', y: 15 },
                ]}
                color="#70bbfd"
              />
              <VerticalBarSeries
                data={[
                  { x: 'A', y: 12 },
                  { x: 'B', y: 2 },
                  { x: 'C', y: 11 },
                ]}
                color="#c88ffa"
              />
            </FlexibleWidthXYPlot>
          </div>
        </CardBody>
      </Card>
    </Col>
  );
};

export default Bar;
