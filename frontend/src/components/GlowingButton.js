import React, { useState } from 'react';

const GlowingButton = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  size = 'medium',
  glowColor = '#00C851',
  disabled = false,
  className = '',
  ...props 
}) => {
  const [isPressed, setIsPressed] = useState(false);
  const [ripples, setRipples] = useState([]);

  const handleClick = (e) => {
    if (disabled) return;
    
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const newRipple = {
      x,
      y,
      id: Date.now()
    };
    
    setRipples(prev => [...prev, newRipple]);
    
    // Remove ripple after animation
    setTimeout(() => {
      setRipples(prev => prev.filter(ripple => ripple.id !== newRipple.id));
    }, 600);
    
    if (onClick) onClick(e);
  };

  const getVariantStyles = () => {
    switch (variant) {
      case 'secondary':
        return {
          background: 'linear-gradient(135deg, #6c757d, #495057)',
          glowColor: '#6c757d'
        };
      case 'success':
        return {
          background: 'linear-gradient(135deg, #28a745, #20c997)',
          glowColor: '#28a745'
        };
      case 'warning':
        return {
          background: 'linear-gradient(135deg, #ffc107, #fd7e14)',
          glowColor: '#ffc107'
        };
      case 'danger':
        return {
          background: 'linear-gradient(135deg, #dc3545, #e83e8c)',
          glowColor: '#dc3545'
        };
      default:
        return {
          background: 'linear-gradient(135deg, #00C851, #00A043)',
          glowColor: glowColor
        };
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return {
          padding: '8px 16px',
          fontSize: '14px',
          minHeight: '36px'
        };
      case 'large':
        return {
          padding: '16px 32px',
          fontSize: '18px',
          minHeight: '56px'
        };
      default:
        return {
          padding: '12px 24px',
          fontSize: '16px',
          minHeight: '48px'
        };
    }
  };

  const variantStyles = getVariantStyles();
  const sizeStyles = getSizeStyles();

  const buttonStyle = {
    position: 'relative',
    border: 'none',
    borderRadius: '12px',
    color: 'white',
    fontWeight: '600',
    cursor: disabled ? 'not-allowed' : 'pointer',
    overflow: 'hidden',
    transition: 'all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
    transform: isPressed ? 'scale(0.95)' : 'scale(1)',
    opacity: disabled ? 0.6 : 1,
    boxShadow: disabled ? 'none' : `0 4px 20px ${variantStyles.glowColor}40`,
    background: variantStyles.background,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    ...sizeStyles
  };

  return (
    <button
      className={`glowing-button ${className}`}
      style={buttonStyle}
      onMouseDown={() => setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
      onMouseLeave={() => setIsPressed(false)}
      onClick={handleClick}
      disabled={disabled}
      {...props}
    >
      {/* Shine effect */}
      <div
        style={{
          position: 'absolute',
          top: '-50%',
          left: '-50%',
          width: '200%',
          height: '200%',
          background: 'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.2) 50%, transparent 70%)',
          animation: 'shine 3s infinite',
          pointerEvents: 'none'
        }}
      />
      
      {/* Ripple effects */}
      {ripples.map(ripple => (
        <span
          key={ripple.id}
          style={{
            position: 'absolute',
            left: ripple.x,
            top: ripple.y,
            width: '10px',
            height: '10px',
            background: 'rgba(255,255,255,0.6)',
            borderRadius: '50%',
            transform: 'translate(-50%, -50%)',
            animation: 'ripple 0.6s linear',
            pointerEvents: 'none'
          }}
        />
      ))}
      
      {children}
      
      <style jsx>{`
        @keyframes shine {
          0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
          100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        
        @keyframes ripple {
          0% {
            transform: translate(-50%, -50%) scale(1);
            opacity: 1;
          }
          100% {
            transform: translate(-50%, -50%) scale(20);
            opacity: 0;
          }
        }
        
        .glowing-button:hover {
          box-shadow: 0 8px 30px ${variantStyles.glowColor}60 !important;
          transform: translateY(-2px) scale(1.02) !important;
        }
        
        .glowing-button:active {
          transform: scale(0.98) !important;
        }
      `}</style>
    </button>
  );
};

export default GlowingButton;