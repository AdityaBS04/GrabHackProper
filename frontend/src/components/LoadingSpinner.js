import React from 'react';

const LoadingSpinner = ({ text = "Loading..." }) => {
  return (
    <div className="fancy-loading">
      <div className="loading-spinner">
        <div className="loading-ring"></div>
        <div className="loading-ring"></div>
        <div className="loading-ring"></div>
      </div>
      <div className="loading-text">{text}</div>
    </div>
  );
};

export default LoadingSpinner;