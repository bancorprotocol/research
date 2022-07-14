import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { useTranslation } from 'react-i18next';
import {
  PieChart, Pie, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import Panel from '@/shared/components/Panel';
import getTooltipStyles from '@/shared/helpers';

const Withdrawals = ({ dir, themeName }) => {
  const { t } = useTranslation('common');
  const [coordinates, setCoordinates] = useState({ x: 0, y: 0 });

  const onMouseMove = (e) => {
    if (e.tooltipPosition) {
      setCoordinates({ x: dir === 'ltr' ? e.tooltipPosition.x : e.tooltipPosition.x / 10, y: e.tooltipPosition.y });
    }
  };

  return (
    <Panel
      lg={6}
      xl={4}
      md={12}
      title="Withdrawals"
      subhead="By status"
    >
      <div className="dashboard__visitors-chart">
        <ResponsiveContainer className="dashboard__chart-pie" width="100%" height={220}>
          <p className="plyr__video-embed">
            {/* eslint-disable-next-line max-len */}
            <iframe src="https://public.tableau.com/views/UI-test/Withdrawals?:showVizHome=no&:embed=true&:toolbar=no&:showShareOptions=false&:display_count=no&:showDataDetails=no&:showAppBanner=false" width="100%" height={220} frameBorder="0" scrolling="yes" title="Withdrawals" />
          </p>
        </ResponsiveContainer>
      </div>
    </Panel>
  );
};

Withdrawals.propTypes = {
  dir: PropTypes.string.isRequired,
  themeName: PropTypes.string.isRequired,
};

export default connect(state => ({ themeName: state.theme.className }))(Withdrawals);
