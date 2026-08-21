import React from 'react';

export function LoadingSkeleton() {
  return (
    <div className="glass-card" style={{ opacity: 0.7, padding: '1.5rem' }}>
      <div style={{ width: '40%', height: '1.25rem', background: 'rgba(255,255,255,0.08)', borderRadius: '6px', marginBottom: '1rem' }}></div>
      <div style={{ width: '70%', height: '2rem', background: 'rgba(255,255,255,0.12)', borderRadius: '8px', marginBottom: '0.75rem' }}></div>
      <div style={{ width: '50%', height: '1rem', background: 'rgba(255,255,255,0.08)', borderRadius: '6px', marginBottom: '1rem' }}></div>
      <div style={{ width: '30%', height: '2.5rem', background: 'rgba(99, 102, 241, 0.2)', borderRadius: '12px' }}></div>
    </div>
  );
}
