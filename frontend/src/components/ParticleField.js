import React, { useEffect, useRef, useState } from 'react';

const ParticleField = ({ particleCount = 50, color = "#00C851", speed = 0.5 }) => {
  const canvasRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const particles = useRef([]);
  const animationFrame = useRef(null);

  useEffect(() => {
    const updateDimensions = () => {
      if (canvasRef.current) {
        const { width, height } = canvasRef.current.getBoundingClientRect();
        setDimensions({ width, height });
        canvasRef.current.width = width;
        canvasRef.current.height = height;
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !dimensions.width || !dimensions.height) return;

    const ctx = canvas.getContext('2d');
    
    // Initialize particles
    particles.current = Array.from({ length: particleCount }, () => ({
      x: Math.random() * dimensions.width,
      y: Math.random() * dimensions.height,
      vx: (Math.random() - 0.5) * speed,
      vy: (Math.random() - 0.5) * speed,
      radius: Math.random() * 3 + 1,
      opacity: Math.random() * 0.5 + 0.3,
      life: Math.random() * 100 + 100
    }));

    const animate = () => {
      ctx.clearRect(0, 0, dimensions.width, dimensions.height);
      
      particles.current.forEach((particle, index) => {
        // Update position
        particle.x += particle.vx;
        particle.y += particle.vy;
        particle.life--;

        // Bounce off walls
        if (particle.x <= 0 || particle.x >= dimensions.width) particle.vx *= -1;
        if (particle.y <= 0 || particle.y >= dimensions.height) particle.vy *= -1;

        // Reset particle if it dies
        if (particle.life <= 0) {
          particle.x = Math.random() * dimensions.width;
          particle.y = Math.random() * dimensions.height;
          particle.life = Math.random() * 100 + 100;
          particle.opacity = Math.random() * 0.5 + 0.3;
        }

        // Draw particle
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
        ctx.fillStyle = color + Math.floor(particle.opacity * 255).toString(16).padStart(2, '0');
        ctx.fill();

        // Draw connections to nearby particles
        particles.current.slice(index + 1).forEach(otherParticle => {
          const dx = particle.x - otherParticle.x;
          const dy = particle.y - otherParticle.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          
          if (distance < 100) {
            ctx.beginPath();
            ctx.moveTo(particle.x, particle.y);
            ctx.lineTo(otherParticle.x, otherParticle.y);
            ctx.strokeStyle = color + Math.floor((1 - distance / 100) * 50).toString(16).padStart(2, '0');
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        });
      });

      animationFrame.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationFrame.current) {
        cancelAnimationFrame(animationFrame.current);
      }
    };
  }, [dimensions, particleCount, color, speed]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: -1,
        opacity: 0.6
      }}
    />
  );
};

export default ParticleField;