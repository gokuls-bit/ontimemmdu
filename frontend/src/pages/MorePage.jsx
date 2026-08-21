import React from 'react';
import { TimetableDownloads } from '../components/downloads/TimetableDownloads';
import { User, Clock, ShieldCheck, RefreshCw, Settings, Info } from 'lucide-react';

export function MorePage({ context, onOpenContextModal, serverTime }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Active Academic Context Card */}
      <div className="glass-card" style={{ borderLeft: '4px solid #8b5cf6' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            <User size={16} /> ACTIVE ACADEMIC CONTEXT
          </div>
          <button
            onClick={onOpenContextModal}
            style={{
              background: 'rgba(139, 92, 246, 0.15)',
              border: '1px solid rgba(139, 92, 246, 0.35)',
              color: '#c084fc',
              padding: '0.35rem 0.75rem',
              borderRadius: '8px',
              fontWeight: 700,
              fontSize: '0.8rem',
              cursor: 'pointer',
            }}
          >
            Change
          </button>
        </div>

        <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc' }}>
          {context?.semester}th Semester • {context?.section} {context?.group ? `(Group ${context.group})` : ''}
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
          Saved locally in browser memory for instant timetable lookup.
        </p>
      </div>

      {/* Official Timetable Downloads Hub */}
      <TimetableDownloads />

      {/* System Status & Authoritative Server Time */}
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
          <Info size={16} /> SYSTEM INFORMATION
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Server Clock:</span>
            <strong style={{ color: '#38bdf8' }}>{serverTime || 'Live (Asia/Kolkata)'}</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Timezone Standard:</span>
            <strong style={{ color: '#fff' }}>IST / India Standard Time</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Department:</span>
            <strong style={{ color: '#fff' }}>CSE Department</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
