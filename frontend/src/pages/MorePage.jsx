import React from 'react';
import { TimetableDownloads } from '../components/downloads/TimetableDownloads';
import { User, Clock, ShieldCheck, RefreshCw, Settings, Info, Sun, Moon, Laptop, Building, Compass } from 'lucide-react';

export function MorePage({ context, onOpenContextModal, serverTime, theme, onToggleTheme }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Active Academic Context Card */}
      <div className="glass-card" style={{ borderLeft: '4px solid var(--accent-primary)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            <User size={16} /> YOUR ACTIVE SECTION
          </div>
          <button
            onClick={onOpenContextModal}
            style={{
              background: 'var(--status-active-bg)',
              border: '1px solid rgba(139, 92, 246, 0.35)',
              color: 'var(--status-active)',
              padding: '0.35rem 0.85rem',
              borderRadius: '10px',
              fontWeight: 800,
              fontSize: '0.8rem',
              cursor: 'pointer',
            }}
          >
            Edit Preferences
          </button>
        </div>

        <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-primary)' }}>
          {context?.semester}th Semester • {context?.section} {context?.group ? `(Group ${context.group})` : ''}
        </h3>
        <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
          Department of Computer Science & Engineering, MMDU Campus.
        </p>
      </div>

      {/* Theme Customization Option */}
      <div className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: 'var(--status-active-bg)', color: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {theme === 'dark' ? <Moon size={20} /> : <Sun size={20} />}
          </div>
          <div>
            <h4 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-primary)' }}>
              App Color Theme
            </h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              {theme === 'dark' ? 'Dark Mode Active' : 'Light Mode Active'}
            </p>
          </div>
        </div>

        <button
          onClick={onToggleTheme}
          style={{
            background: 'var(--bg-input)',
            border: '1px solid var(--glass-border)',
            color: 'var(--text-primary)',
            padding: '0.5rem 1rem',
            borderRadius: '10px',
            fontWeight: 800,
            fontSize: '0.85rem',
            cursor: 'pointer',
          }}
        >
          {theme === 'dark' ? '☀️ Switch to Light' : '🌙 Switch to Dark'}
        </button>
      </div>

      {/* Official Timetable Downloads Hub */}
      <TimetableDownloads />

      {/* System Information Card */}
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.85rem' }}>
          <Info size={16} /> SYSTEM INFORMATION & CLOCK
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.88rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Authoritative Server Time:</span>
            <strong style={{ color: 'var(--accent-primary)' }}>{serverTime || 'Live Sync (Asia/Kolkata)'}</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Campus Time Zone:</span>
            <strong style={{ color: 'var(--text-primary)' }}>IST (UTC +5:30)</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Department:</span>
            <strong style={{ color: 'var(--text-primary)' }}>CSE Department (MMDU Mullana)</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>App Version:</span>
            <strong style={{ color: 'var(--status-free)' }}>MMDU Central v2.0 (Human Release)</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
