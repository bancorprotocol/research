import React from 'react';
import PropTypes from 'prop-types';
import SidebarLink from './SidebarLink';
import SidebarCategory from './SidebarCategory';

const SidebarContent = ({
  onClick, changeToLight, changeToDark, sidebarCollapse,
}) => (
  <div className="sidebar__content">
    <ul className="sidebar__block">
      <SidebarLink
        title="Home"
        icon="home"
        route="/online_marketing_dashboard"
        onClick={onClick}
      />
    </ul>
  </div>
);

SidebarContent.propTypes = {
  changeToDark: PropTypes.func.isRequired,
  changeToLight: PropTypes.func.isRequired,
  onClick: PropTypes.func,
  sidebarCollapse: PropTypes.bool,
};

SidebarContent.defaultProps = {
  sidebarCollapse: false,
  onClick: () => {},
};

export default SidebarContent;
