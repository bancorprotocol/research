import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { useTranslation } from 'react-i18next';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import Panel from '@/shared/components/Panel';
import getTooltipStyles from '@/shared/helpers';

const SelectMetric = ({ dir, themeName }) => {
  const { t } = useTranslation('common');

  return (
    <Panel md={12} lg={12} xl={12} title="Select Metrics">
      <div dir="ltr">
        <ResponsiveContainer height={650} className="plyr__video-embed">
          {/* eslint-disable-next-line max-len */}
          <iframe src="https://public.tableau.com/views/UI-test/MainDashboard?:showVizHome=no&:embed=true&:toolbar=no" frameBorder="0" scrolling="no" title="MainDashboard" />
        </ResponsiveContainer>
      </div>
    </Panel>
  );
};


SelectMetric.propTypes = {
  dir: PropTypes.string.isRequired,
  themeName: PropTypes.string.isRequired,
};

export default connect(state => ({ themeName: state.theme.className }))(SelectMetric);
