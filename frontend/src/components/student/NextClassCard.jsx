import React from 'react';
import { ArrowRight, MapPin, User, Clock, CheckCircle2 } from 'lucide-react';

export function NextClassCard({ nextClass, onGoToRoom }) {
  if (!nextClass || nextClass.status === 'NO_MORE_CLASSES') {
    return (
      <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
        <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: 'var(--status-free-bg)', color: 'var(--status-free)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <CheckCircle2 size={22} />
        </div>
        <div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            All Set For Today! 🎉
          </h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            No more classes left on your schedule today. Time to relax or hit the library.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card" style={{ borderLeft: '4px solid var(--accent-primary)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <h4 style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--accent-primary)', letterSpacing: '0.06em' }}>
          UP NEXT
        </h4>
        {nextClass.minutes_until_start !== undefined && (
          <span style={{ fontSize: '0.78rem', fontWeight: 800, color: 'var(--status-break)', background: 'var(--status-break-bg)', padding: '0.2rem 0.6rem', borderRadius: '8px', border: '1px solid rgba(59, 130, 246, 0.25)' }}>
            Starts in {nextClass.minutes_until_start} mins
          </span>
        )}
      </div>

      <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
        {nextClass.subject_name || nextClass.subject}
      </h3>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '1rem' }}>
        {nextClass.teacher && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <User size={15} style={{ color: 'var(--accent-primary)' }} />
            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{nextClass.teacher}</span>
          </div>
        )}
        {nextClass.start_time && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Clock size={15} style={{ color: 'var(--accent-primary)' }} />
            <span>{nextClass.start_time} — {nextClass.end_time}</span>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.75rem', borderTop: '1px solid var(--glass-border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <MapPin size={18} style={{ color: 'var(--accent-primary)' }} />
          <span style={{ fontWeight: 800, fontSize: '1.1rem', color: 'var(--status-active)' }}>
            ROOM {nextClass.room}
          </span>
        </div>

        {onGoToRoom && nextClass.room && (
          <button
            onClick={() => onGoToRoom(nextClass.room)}
            style={{
              background: 'var(--status-active-bg)',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              color: 'var(--status-active)',
              padding: '0.4rem 0.85rem',
              borderRadius: '10px',
              fontWeight: 700,
              fontSize: '0.82rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            Find Room <ArrowRight size={15} />
          </button>
        )}
      </div>
    </div>
  );
}
