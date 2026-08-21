import React from 'react';
import { Compass, Clock, RefreshCw, UserCheck } from 'lucide-react';

export function Navbar({ context, onOpenContextModal, onRefresh, loading, lastUpdated }) {
  return (
    <header className="navbar-header">
      <div className="brand-title">
        <Compass className="w-6 h-6 text-indigo-400" />
        <span>CSE SmartRoom</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {context && (
          <button
            onClick={onOpenContextModal}
            style={{
              background: 'rgba(99, 102, 241, 0.12)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              borderRadius: '9999px',
              padding: '0.3rem 0.75rem',
              color: '#a78bfa',
              fontSize: '0.8rem',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              cursor: 'pointer',
            }}
          >
            <UserCheck size={14} />
            <span>{context.semester} - {context.section} {context.group ? `(${context.group})` : ''}</span>
          </button>
        )}

        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={loading}
            title={`Last updated ${lastUpdated || 'just now'}`}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
          </button>
        )}
      </div>
    </header>
  );
}
