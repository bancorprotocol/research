import React from 'react';
import { Route, Switch } from 'react-router-dom';
import FinanceDashboard from '../../../Dashboards/archive/Finance/index';
import FinanceDashboardEdit from '../../../Dashboards/archive/FinanceTableEdit/index';

export default () => (
  <Switch>
    <Route exact path="/finance_dashboard" component={FinanceDashboard} />
    <Route path="/finance_dashboard/edit/:index" component={FinanceDashboardEdit} />
  </Switch>
);
