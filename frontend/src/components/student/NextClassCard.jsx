import React from 'react';
import { ArrowRight, MapPin, User, Clock } from 'lucide-react';

export function NextClassCard({ nextClass, onGoToRoom }) {
  if (!nextClass || nextClass.status === 'NO_MORE_CLASSES') {
    return (
      <div className="glass-card" style={{ opacity: 0.8 }}>
        <h4 style={{ fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
          NEXT CLASS
        </h4>
        <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>
          No more classes scheduled for the remainder of today.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-card" style={{ borderLeft: '4px solid #6366f1' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <h4 style={{ fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: '#a78bfa', letterSpacing: '0.05em' }}>
          UPCOMING NEXT
        </h4>
        {nextClass.minutes_until_start !== undefined && (
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#38bdf8', background: 'rgba(56, 189, 248, 0.12)', padding: '0.2rem 0.6rem', borderRadius: '6px' }}>
            Starts in {nextClass.minutes_until_start} min
          </span>
        )}
      </div>

      <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.4rem' }}>
        {nextClass.subject_name || nextClass.subject}
      </h3>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1rem' }}>
        {nextClass.teacher && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <User size={15} className="text-indigo-400" />
            <span>{nextClass.teacher}</span>
          </div>
        )}
        {nextClass.start_time && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Clock size={15} className="text-indigo-400" />
            <span>{nextClass.start_time} — {nextClass.end_time}</span>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.75rem', borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <MapPin size={18} className="text-indigo-400" />
          <span style={{ fontWeight: 800, fontSize: '1.1rem', color: '#c084fc' }}>
            ROOM {nextClass.room}
          </span>
        </div>

        {onGoToRoom && nextClass.room && (
          <button
            onClick={() => onGoToRoom(nextClass.room)}
            style={{
              background: 'rgba(99, 102, 241, 0.15)',
              border: '1px solid rgba(99, 102, 241, 0.35)',
              color: '#a78bfa',
              padding: '0.4rem 0.85rem',
              borderRadius: '8px',
              fontWeight: 700,
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            GO TO ROOM <ArrowRight size={16} />
          </button>
        )}
      </div>
    </div>
  );
}
