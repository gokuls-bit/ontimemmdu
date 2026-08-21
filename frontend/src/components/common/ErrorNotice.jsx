import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export function ErrorNotice({ message, onRetry }) {
  return (
    <div className="glass-card" style={{ borderLeft: '4px solid #ef4444', padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
        <AlertTriangle className="text-red-400" size={24} style={{ flexShrink: 0 }} />
        <div style={{ flexGrow: 1 }}>
          <h4 style={{ color: '#f87171', fontSize: '1rem', fontWeight: 700, marginBottom: '0.25rem' }}>
            Connection Error
          </h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.75rem' }}>
            {message || 'SmartRoom is temporarily unable to connect to the server.'}
          </p>
          {onRetry && (
            <button
              onClick={onRetry}
              style={{
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                color: '#f87171',
                padding: '0.4rem 0.8rem',
                borderRadius: '8px',
                fontSize: '0.8rem',
                fontWeight: 600,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                cursor: 'pointer',
              }}
            >
              <RefreshCw size={14} /> Retry
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
