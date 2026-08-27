import React from 'react';
import { Compass, RefreshCw, UserCheck, Sun, Moon, Sparkles } from 'lucide-react';

export function Navbar({ context, onOpenContextModal, onRefresh, loading, lastUpdated, theme, onToggleTheme }) {
  return (
    <header className="navbar-header">
      {/* Brand Title */}
      <div className="brand-title">
        <div className="brand-logo-icon">
          <Compass size={20} />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '1.2rem', color: 'var(--text-primary)' }}>
              MMDU Central
            </span>
            <span
              style={{
                fontSize: '0.65rem',
                fontWeight: 700,
                padding: '0.15rem 0.45rem',
                borderRadius: '9999px',
                background: 'var(--status-free-bg)',
                color: 'var(--status-free)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.25rem',
              }}
            >
              <span className="pulse-dot" style={{ width: '5px', height: '5px' }}></span>
              Live
            </span>
          </div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 500, marginTop: '-2px' }}>
            CSE Smart Room Portal
          </span>
        </div>
      </div>

      {/* Action Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        {/* Student Section Badge */}
        {context && (
          <button
            onClick={onOpenContextModal}
            style={{
              background: 'var(--status-active-bg)',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              borderRadius: '9999px',
              padding: '0.35rem 0.75rem',
              color: 'var(--status-active)',
              fontSize: '0.8rem',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            title="Change semester & section"
          >
            <UserCheck size={14} />
            <span>{context.semester}th Sem • {context.section}</span>
          </button>
        )}

        {/* Light / Dark Theme Switcher */}
        <button
          onClick={onToggleTheme}
          style={{
            background: 'var(--bg-input)',
            border: '1px solid var(--glass-border)',
            borderRadius: '50%',
            width: '36px',
            height: '36px',
            color: 'var(--text-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
          title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {theme === 'dark' ? <Sun size={18} className="text-amber-400" /> : <Moon size={18} className="text-indigo-600" />}
        </button>

        {/* Refresh Data Button */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={loading}
            title={`Last updated ${lastUpdated || 'just now'}`}
            style={{
              background: 'var(--bg-input)',
              border: '1px solid var(--glass-border)',
              borderRadius: '50%',
              width: '36px',
              height: '36px',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s ease',
            }}
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        )}
      </div>
    </header>
  );
}
