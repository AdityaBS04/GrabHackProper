import React from 'react';

const FloatingActionButton = ({ onClick, icon = "💬", hidden = false }) => {
  if (hidden) return null;

  return (
    <button 
      className="floating-action-btn"
      onClick={onClick}
      aria-label="Quick Action"
    >
      {icon}
    </button>
  );
};

export default FloatingActionButton;