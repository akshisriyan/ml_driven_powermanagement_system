import React from 'react';

const LogoIcon = ({ className = '', size = 36, color = '#0d9488', accent = '#2563eb', title = 'PowerGrid' }) => (
  <svg
    className={className}
    role="img"
    aria-label={title}
    width={size}
    height={size}
    viewBox="0 0 64 64"
    xmlns="http://www.w3.org/2000/svg"
  >
    <title>{title}</title>
    <defs>
      <linearGradient id="pg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor={color} />
        <stop offset="100%" stopColor={accent} />
      </linearGradient>
    </defs>
    {/* Outer ring */}
    <circle cx="32" cy="32" r="30" fill="#ffffff" stroke="url(#pg-grad)" strokeWidth="4" />
    {/* Bolt */}
    <path
      d="M34 6 L14 38 H28 L22 58 L50 26 H36 L42 6 Z"
      fill="url(#pg-grad)"
      stroke="none"
    />
  </svg>
);

export default LogoIcon;
