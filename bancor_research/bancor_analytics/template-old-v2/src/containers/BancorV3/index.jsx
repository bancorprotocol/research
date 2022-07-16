import React from 'react';
import { compose } from 'redux';
import { connect } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { Col, Container, Row } from 'reactstrap';
import { RTLProps } from '@/shared/prop-types/ReducerProps2';
import SurplusStat from './components/SurplusStat';
// import PriorDayFees from './components/PriorDayFees';
// import ProtocolStakedBalance from './components/ProtocolStakedBalance';
// import ProtocolVaultBalance from './components/ProtocolVaultBalance';
// import SelectMetric from './components/SelectMetric';
// import BounceRateArea from './components/WithdrawalsRatio';
// import Withdrawals from './components/Withdrawals';
// import SalesStatistic from './components/SalesStatistic';
// import BudgetStatistic from './components/BudgetStatistic';
// import PoolInfo from './components/PoolInfo';
// import BestSellingRegions from './components/BestSellingRegions';
// import GoalsCompletion from './components/GoalsCompletion';
import ExampleCard from './components/ExampleCard';


const BancorV3 = ({ rtl }) => {
  const { t } = useTranslation('common');
  return (
    <Container className="dashboard">
      <Row>
        <ExampleCard />
        <Col md={12}>
          <h3 className="page-title">hi</h3>
        </Col>
      </Row>
      <Row>
        <SurplusStat />
      </Row>
    </Container>
  );
};

BancorV3.propTypes = {
  rtl: RTLProps.isRequired,
};

export default compose(connect(state => ({
  rtl: state.rtl,
})))(BancorV3);
