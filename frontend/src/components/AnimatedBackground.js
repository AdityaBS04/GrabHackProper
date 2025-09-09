import React, { useEffect, useState } from 'react';

const AnimatedBackground = () => {
  const [particles, setParticles] = useState([]);

  useEffect(() => {
    // Generate random particles
    const generateParticles = () => {
      const newParticles = [];
      for (let i = 0; i < 15; i++) {
        newParticles.push({
          id: i,
          left: Math.random() * 100,
          delay: Math.random() * 8,
          duration: 6 + Math.random() * 4,
          size: 4 + Math.random() * 8,
          opacity: 0.3 + Math.random() * 0.5
        });
      }
      setParticles(newParticles);
    };

    generateParticles();
    
    // Regenerate particles every 30 seconds for variety
    const interval = setInterval(generateParticles, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="floating-particles">
      {particles.map((particle) => (
        <div
          key={particle.id}
          className="particle"
          style={{
            left: `${particle.left}%`,
            animationDelay: `-${particle.delay}s`,
            animationDuration: `${particle.duration}s`,
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            opacity: particle.opacity
          }}
        />
      ))}
    </div>
  );
};

export default AnimatedBackground;