import React from 'react';

const Navbar = ({ user, onLogout, onNavigate, current }) => {
  const links = [
    { key: 'dashboard', label: 'Dashboard', roles: ['admin','client'] },
    { key: 'data', label: 'Data', roles: ['admin'] },
    { key: 'models', label: 'Models', roles: ['admin'] },
    { key: 'health', label: 'Health', roles: ['admin','client'] },
  ];

  return (
    <nav className="navbar">
      <div className="nav-left">
        <div className="brand">⚡ PowerGrid</div>
        <ul className="nav-links">
          {links.filter(l => l.roles.includes(user.role)).map(l => (
            <li key={l.key} className={current === l.key ? 'active' : ''}>
              <button onClick={() => onNavigate(l.key)}>{l.label}</button>
            </li>
          ))}
        </ul>
      </div>
      <div className="nav-right">
        <div className="user-info">
          <span className="user-name">{user.username}</span>
          <span className={`role-badge role-${user.role}`}>{user.role}</span>
        </div>
        <button className="logout-btn" onClick={onLogout}>Logout</button>
      </div>
    </nav>
  );
};

export default Navbar;
