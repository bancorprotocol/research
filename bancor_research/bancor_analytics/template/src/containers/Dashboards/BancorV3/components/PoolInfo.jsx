import React from 'react';
import { useTranslation } from 'react-i18next';
import { Progress, Table } from 'reactstrap';
import Panel from '@/shared/components/Panel';


const PoolInfo = () => {
  const { t } = useTranslation('common');

  return (
    <Panel responsive lg={12} xl={8} md={12} title="Pool Info">
      {/* <TrendingDownIcon className="dashboard__trend-icon" /> */}
      <p className="plyr__video-embed">
        {/* eslint-disable-next-line max-len */}
        <iframe src="https://public.tableau.com/views/UI-test/PoolInfo?:showVizHome=no&:embed=true&:toolbar=no" width="100%" height={320} frameBorder="0" scrolling="no" title="PoolInfo" />
      </p>
    </Panel>
  );
};

export default PoolInfo;
