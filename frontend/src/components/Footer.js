import React from 'react';

const Footer = () => (
  <footer className="footer">
    <div className="footer-content">
      <span>© {new Date().getFullYear()} ML Power Grid</span>
      <span className="sep">|</span>
      <span>AI-driven monitoring</span>
    </div>
  </footer>
);

export default Footer;
