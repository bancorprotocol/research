import React from 'react';
import PropTypes from 'prop-types';
import { NavLink } from 'react-router-dom';
import { Badge } from 'reactstrap';

const TopbarNavLink = ({
  title, icon, newLink, route,
}) => (
  <NavLink className="topbar__link" to={route}>
    {icon ? <span className={`topbar__link-icon lnr lnr-${icon}`} /> : ''}
    <p className="topbar__link-title">
      {title}
      {newLink ? <Badge className="topbar__link-badge"><span>New</span></Badge> : ''}
    </p>
  </NavLink>
);

TopbarNavLink.propTypes = {
  title: PropTypes.string.isRequired,
  icon: PropTypes.string,
  newLink: PropTypes.bool,
  route: PropTypes.string.isRequired,
};

TopbarNavLink.defaultProps = {
  icon: '',
  newLink: false,
};

export default TopbarNavLink;
