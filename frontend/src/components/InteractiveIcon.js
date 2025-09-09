import React, { useState } from 'react';

const InteractiveIcon = ({ icon, size = 24, onClick, hoverColor = "#00C851", className = "" }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isClicked, setIsClicked] = useState(false);

  const handleClick = () => {
    setIsClicked(true);
    setTimeout(() => setIsClicked(false), 200);
    if (onClick) onClick();
  };

  const iconStyle = {
    fontSize: `${size}px`,
    cursor: 'pointer',
    display: 'inline-block',
    transition: 'all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
    transform: isClicked ? 'scale(0.8)' : isHovered ? 'scale(1.2) rotate(5deg)' : 'scale(1)',
    color: isHovered ? hoverColor : 'inherit',
    filter: isHovered ? 'drop-shadow(0 4px 8px rgba(0,200,81,0.3))' : 'none',
    animation: isClicked ? 'bounce 0.3s ease' : 'none'
  };

  return (
    <span
      className={`interactive-icon ${className}`}
      style={iconStyle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyPress={(e) => e.key === 'Enter' && handleClick()}
    >
      {icon}
    </span>
  );
};

export default InteractiveIcon;