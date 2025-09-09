import React from 'react';

const PulsingOrb = ({ 
  size = 100, 
  color = '#00C851', 
  intensity = 0.8, 
  speed = 2,
  className = '',
  style = {},
  ...props 
}) => {
  const orbStyle = {
    width: `${size}px`,
    height: `${size}px`,
    borderRadius: '50%',
    background: `radial-gradient(circle at 30% 30%, ${color}40, ${color}80, ${color})`,
    position: 'relative',
    animation: `orbPulse ${speed}s ease-in-out infinite`,
    boxShadow: `
      0 0 ${size * 0.2}px ${color}60,
      0 0 ${size * 0.4}px ${color}40,
      0 0 ${size * 0.6}px ${color}20,
      inset 0 0 ${size * 0.1}px rgba(255,255,255,0.3)
    `,
    ...style
  };

  const innerOrbStyle = {
    position: 'absolute',
    top: '20%',
    left: '20%',
    width: '60%',
    height: '60%',
    borderRadius: '50%',
    background: `radial-gradient(circle at 40% 40%, rgba(255,255,255,0.8), transparent 60%)`,
    animation: `innerGlow ${speed * 1.5}s ease-in-out infinite`
  };

  const sparkleStyle = {
    position: 'absolute',
    top: '10%',
    right: '25%',
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: 'rgba(255,255,255,0.9)',
    animation: `sparkle ${speed * 0.8}s ease-in-out infinite alternate`
  };

  return (
    <>
      <div className={`pulsing-orb ${className}`} style={orbStyle} {...props}>
        <div style={innerOrbStyle} />
        <div style={sparkleStyle} />
      </div>
      
      <style jsx>{`
        @keyframes orbPulse {
          0%, 100% {
            transform: scale(1);
            opacity: ${intensity};
          }
          50% {
            transform: scale(1.1);
            opacity: ${intensity * 1.2};
            box-shadow: 
              0 0 ${size * 0.3}px ${color}80,
              0 0 ${size * 0.5}px ${color}60,
              0 0 ${size * 0.8}px ${color}40,
              inset 0 0 ${size * 0.15}px rgba(255,255,255,0.4);
          }
        }
        
        @keyframes innerGlow {
          0%, 100% {
            opacity: 0.6;
            transform: scale(1);
          }
          50% {
            opacity: 0.9;
            transform: scale(1.2);
          }
        }
        
        @keyframes sparkle {
          0% {
            opacity: 0.3;
            transform: scale(0.8);
          }
          100% {
            opacity: 1;
            transform: scale(1.2);
          }
        }
      `}</style>
    </>
  );
};

export default PulsingOrb;