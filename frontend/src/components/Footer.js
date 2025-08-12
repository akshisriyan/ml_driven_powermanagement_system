import React from 'react';
import { NavLink } from 'react-router-dom';
import LogoIcon from './LogoIcon';

const Footer = () => {
  const year = new Date().getFullYear();
  return (
    <footer className="footer light" role="contentinfo">
      <div className="footer-inner">
        <div className="footer-brand">
          <LogoIcon className="footer-logo" size={40} />
          <div className="brand-text">
            <span className="brand-name">PowerGrid</span>
            <span className="brand-tag">ML Energy Intelligence</span>
          </div>
        </div>
        <nav className="footer-nav" aria-label="Footer Navigation">
          <NavLink to="/" aria-label="Dashboard">Dashboard</NavLink>
          <NavLink to="/analytics" aria-label="Analytics">Analytics</NavLink>
          <NavLink to="/billing" aria-label="Billing">Billing</NavLink>
          <NavLink to="/models" aria-label="Models">Models</NavLink>
          <NavLink to="/health" aria-label="Status">Status</NavLink>
        </nav>
        <div className="footer-meta">
          <span>© {year} PowerGrid</span>
          <span className="sep">•</span>
          <button type="button" className="link-like" aria-label="Privacy Policy">Privacy</button>
          <span className="sep">•</span>
          <button type="button" className="link-like" aria-label="Terms of Service">Terms</button>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
