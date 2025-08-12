import React from 'react';
import { NavLink } from 'react-router-dom';
import LogoIcon from './LogoIcon';

const Navbar = ({ user, onLogout }) => {
  const links = [
    { to: '/', label: 'Dashboard', roles: ['admin','client'] },
    { to: '/analytics', label: 'Analytics', roles: ['admin','client'] },
  { to: '/billing', label: 'Billing', roles: ['admin','client'] },
    { to: '/data', label: 'Data', roles: ['admin'] },
    { to: '/models', label: 'Models', roles: ['admin'] },
    { to: '/health', label: 'Health', roles: ['admin','client'] },
  ];

  return (
    <nav className="navbar light" aria-label="Main Navigation">
      <div className="nav-inner">
        <div className="nav-left">
          <div className="brand" aria-label="Application Name">
            <LogoIcon className="nav-logo" size={34} />
            <span>PowerGrid</span>
          </div>
          <ul className="nav-links" role="menubar">
            {links.filter(l => l.roles.includes(user.role)).map(l => (
              <li key={l.to} role="none">
                <NavLink
                  to={l.to}
                  role="menuitem"
                  className={({ isActive }) => isActive ? 'active' : ''}
                >
                  {l.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
        <div className="nav-right">
          <div className="user-info" aria-label="User Details">
            <span className="user-name">{user.username}</span>
            <span className={`role-badge role-${user.role}`}>{user.role}</span>
          </div>
          <button className="logout-btn" onClick={onLogout} aria-label="Logout">Logout</button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
