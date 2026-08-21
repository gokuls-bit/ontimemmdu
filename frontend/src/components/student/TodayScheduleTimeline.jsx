import React from 'react';
import { StatusBadge } from '../common/StatusBadge';
import { Clock, MapPin, User } from 'lucide-react';

export function TodayScheduleTimeline({ schedule }) {
  if (!schedule || schedule.length === 0) {
    return (
      <div className="glass-card" style={{ textAlign: 'center', padding: '2rem' }}>
        <p style={{ color: 'var(--text-secondary)' }}>No timetable entries available for today.</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {schedule.map((entry, idx) => {
        const isCurrent = entry.status === 'CURRENT' || entry.status === 'ACTIVE_CLASS';
        const isCompleted = entry.status === 'COMPLETED';
        const isFree = entry.status === 'FREE';
        const isCancelled = entry.status === 'CANCELLED';

        return (
          <div
            key={idx}
            className="glass-card"
            style={{
              padding: '1rem',
              opacity: isCompleted ? 0.65 : 1,
              borderLeft: isCurrent
                ? '4px solid #8b5cf6'
                : isCompleted
                ? '4px solid #64748b'
                : isFree
                ? '4px solid #10b981'
                : isCancelled
                ? '4px solid #ef4444'
                : '1px solid var(--glass-border)',
              background: isCurrent ? 'rgba(139, 92, 246, 0.08)' : 'var(--bg-card)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                <Clock size={14} />
                <span>P{entry.period} ({entry.start_time} — {entry.end_time})</span>
              </div>
              <StatusBadge status={entry.status} />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: isCancelled ? '#f87171' : '#f8fafc' }}>
                  {isCancelled ? `[CANCELLED] ${entry.subject || ''}` : (entry.subject || 'Free Period')}
                </h4>
                {entry.teacher && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                    <User size={14} className="text-indigo-400" />
                    <span>{entry.teacher}</span>
                  </div>
                )}
              </div>

              {entry.room && (
                <div style={{ textAlign: 'right' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: '#c084fc', fontWeight: 800, fontSize: '1rem' }}>
                    <MapPin size={16} />
                    <span>{entry.room}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
