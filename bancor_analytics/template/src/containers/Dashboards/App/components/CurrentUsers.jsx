import React from 'react';
import { useTranslation } from 'react-i18next';
import { PieChart, Pie } from 'recharts';
import Panel from '@/shared/components/Panel';

const pieChartData = [{ value: 60, fill: '#b8e986' },
  { value: 40, fill: '#f2f4f7' }];

const CurrentUsers = () => {
  const { t } = useTranslation('common');

  return (
    <Panel
      lg={6}
      xl={3}
      md={12}
      title={t('app_dashboard.current_users')}
      subhead="Last 10 minutes"
    >
      <div className="dashboard__current-users">
        <div className="dashboard__current-users-chart">
          <PieChart height={150} width={280}>
            <Pie
              data={pieChartData}
              dataKey="value"
              cx={135}
              cy={140}
              startAngle={180}
              endAngle={0}
              innerRadius={100}
              outerRadius={128}
              paddingAngle={0}
            />
          </PieChart>
          <p className="dashboard__current-users-label">345</p>
        </div>
        <div className="dashboard__current-users-info" dir="ltr">
          <p className="dashboard__current-users-day">
            <span>7d min</span>
            <span>0</span>
          </p>
          <p className="dashboard__current-users-day">
            <span>7d max</span>
            <span>500</span>
          </p>
        </div>
      </div>
    </Panel>
  );
};

export default CurrentUsers;
