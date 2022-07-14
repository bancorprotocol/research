import React from 'react';
import { compose } from 'redux';
import { connect } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { Col, Container, Row } from 'reactstrap';
import { RTLProps } from '@/shared/prop-types/ReducerProps';
import SurplusStat from './components/SurplusStat';
import PriorDayFees from './components/PriorDayFees';
import ProtocolStakedBalance from './components/ProtocolStakedBalance';
import ProtocolVaultBalance from './components/ProtocolVaultBalance';
import SelectMetric from './components/SelectMetric';
import BounceRateArea from './components/WithdrawalsRatio';
import Withdrawals from './components/Withdrawals';
import SalesStatistic from './components/SalesStatistic';
import BudgetStatistic from './components/BudgetStatistic';
import PoolInfo from './components/PoolInfo';
import BestSellingRegions from './components/BestSellingRegions';
import GoalsCompletion from './components/GoalsCompletion';


const OnLineMarketingDashboard = ({ rtl }) => {
  const { t } = useTranslation('common');

  return (
    <Container className="dashboard">
      <Row>
        <Col md={12}>
          <h3 className="page-title">{t('bancor_dashboard.page_title')}</h3>
        </Col>
      </Row>
      <Row>
        <SurplusStat />
        <PriorDayFees />
        <ProtocolStakedBalance />
        <ProtocolVaultBalance />
      </Row>
      <Row>
        <SelectMetric dir={rtl.direction} />
        <BounceRateArea dir={rtl.direction} />
        <Withdrawals dir={rtl.direction} />
        <SalesStatistic />
        <BudgetStatistic />
        <PoolInfo />
        <BestSellingRegions />
        <GoalsCompletion />
      </Row>
    </Container>
  );
};

OnLineMarketingDashboard.propTypes = {
  rtl: RTLProps.isRequired,
};

export default compose(connect(state => ({
  rtl: state.rtl,
})))(OnLineMarketingDashboard);
