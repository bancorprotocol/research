import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardBody, Col } from 'reactstrap';
import Slider from '@/shared/components/range_slider/Slider';

const SliderWithoutParams = () => {
  const { t } = useTranslation('common');

  return (
    <Col md={12} lg={6} xs={12}>
      <Card>
        <CardBody>
          <div className="card__title">
            <h5 className="bold-text">{t('ui_elements.range_sliders.slider_without_params')}</h5>
            <h5 className="subhead">Use default slider</h5>
          </div>
          <div dir="ltr">
            <Slider min={0} max={100} />
          </div>
        </CardBody>
      </Card>
    </Col>
  );
};

export default SliderWithoutParams;
