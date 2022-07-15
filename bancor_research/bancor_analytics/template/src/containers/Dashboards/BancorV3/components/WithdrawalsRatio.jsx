import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { useTranslation } from 'react-i18next';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import Panel from '@/shared/components/Panel';
import getTooltipStyles from '@/shared/helpers';

const data = [
  { name: '12.03', uv: 4000 },
  { name: '13.03', uv: 3000 },
  { name: '14.03', uv: 2000 },
  { name: '15.03', uv: 2780 },
  { name: '16.03', uv: 1890 },
  { name: '17.03', uv: 2390 },
  { name: '18.03', uv: 3490 },
  { name: '19.03', uv: 3490 },
  { name: '20.03', uv: 3490 },
  { name: '21.03', uv: 3490 },
];

const WithdrawalsRatio = ({ dir, themeName }) => {
  const { t } = useTranslation('common');

  return (
    <Panel xl={5} lg={6} md={12} title="Canceled vs Initiated Withdrawals">
      <p className="plyr__video-embed">
        {/* eslint-disable-next-line max-len */}
        <iframe src="https://public.tableau.com/views/UI-test/WithdrawalsRatio?:showVizHome=no&:embed=true&:toolbar=no" width="100%" frameBorder="0" scrolling="yes" title="WithdrawalsRatio" />
      </p>
      <div dir="ltr">
        <ResponsiveContainer height={220} className="dashboard__area">
          <p className="plyr__video-embed">
            {/* eslint-disable-next-line max-len */}
            <iframe src="https://public.tableau.com/views/UI-test/WithdrawalsTrend?:showVizHome=no&:embed=true&:toolbar=no" width="100%" height={220} frameBorder="0" scrolling="yes" title="WithdrawalsTrend" />
          </p>
        </ResponsiveContainer>
      </div>
    </Panel>
  );
};

WithdrawalsRatio.propTypes = {
  dir: PropTypes.string.isRequired,
  themeName: PropTypes.string.isRequired,
};

export default connect(state => ({ themeName: state.theme.className }))(WithdrawalsRatio);
