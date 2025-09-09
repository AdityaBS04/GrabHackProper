import React, { useState } from 'react';

const AnimatedCard = ({ children, className = '', hoverScale = 1.05, ...props }) => {
  const [isHovered, setIsHovered] = useState(false);

  const cardStyle = {
    background: 'white',
    borderRadius: '20px',
    padding: '24px',
    marginBottom: '16px',
    boxShadow: isHovered 
      ? '0 20px 60px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 200, 81, 0.1)' 
      : '0 8px 32px rgba(0, 0, 0, 0.1)',
    border: '1px solid rgba(0, 200, 81, 0.1)',
    position: 'relative',
    overflow: 'hidden',
    transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
    transform: isHovered ? `translateY(-8px) scale(${hoverScale})` : 'translateY(0) scale(1)',
    cursor: 'pointer'
  };

  const glowStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'linear-gradient(135deg, rgba(0, 200, 81, 0.05) 0%, rgba(0, 123, 255, 0.05) 100%)',
    opacity: isHovered ? 1 : 0,
    borderRadius: '20px',
    transition: 'opacity 0.3s ease',
    pointerEvents: 'none'
  };

  const shimmerStyle = {
    position: 'absolute',
    top: '-50%',
    left: isHovered ? '100%' : '-100%',
    width: '100%',
    height: '200%',
    background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent)',
    transform: 'rotate(45deg)',
    transition: 'left 0.6s ease',
    pointerEvents: 'none'
  };

  return (
    <div
      className={`animated-card ${className}`}
      style={cardStyle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      {...props}
    >
      <div style={glowStyle} />
      <div style={shimmerStyle} />
      <div style={{ position: 'relative', zIndex: 1 }}>
        {children}
      </div>
    </div>
  );
};

export default AnimatedCard;