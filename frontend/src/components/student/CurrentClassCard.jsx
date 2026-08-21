import React from 'react';
import { StatusBadge } from '../common/StatusBadge';
import { MapPin, User, Clock, Calendar, Sparkles } from 'lucide-react';
import { useServerClock } from '../../hooks/useServerClock';

export function CurrentClassCard({ currentClass, serverTime }) {
  const { formattedCountdown } = useServerClock(serverTime, currentClass?.minutes_remaining);

  if (!currentClass) return null;

  const status = currentClass.status || 'FREE';
  const isClassActive = status === 'ACTIVE_CLASS';

  return (
    <div
      className="glass-card"
      style={{
        position: 'relative',
        overflow: 'hidden',
        border: isClassActive
          ? '1px solid rgba(139, 92, 246, 0.4)'
          : '1px solid var(--glass-border)',
        boxShadow: isClassActive
          ? '0 12px 36px rgba(139, 92, 246, 0.25)'
          : 'var(--glass-shadow)',
        background: isClassActive
          ? 'linear-gradient(145deg, rgba(19, 27, 46, 0.95) 0%, rgba(30, 27, 75, 0.85) 100%)'
          : 'var(--bg-card)',
      }}
    >
      {/* Top Banner Status */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)' }}>
            CURRENT STATE
          </span>
          <StatusBadge status={status} />
        </div>
        {currentClass.period && (
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#a78bfa', background: 'rgba(167, 139, 250, 0.12)', padding: '0.2rem 0.6rem', borderRadius: '6px' }}>
            Period {currentClass.period}
          </span>
        )}
      </div>

      {/* Main Content View based on State */}
      {isClassActive ? (
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#f8fafc', marginBottom: '0.5rem', lineHeight: 1.2 }}>
            {currentClass.subject_name || currentClass.subject}
          </h2>

          <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '1rem', marginBottom: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            {currentClass.teacher && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <User size={16} className="text-indigo-400" />
                <span style={{ color: '#e2e8f0', fontWeight: 600 }}>{currentClass.teacher}</span>
              </div>
            )}
            {currentClass.start_time && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <Clock size={16} className="text-indigo-400" />
                <span>{currentClass.start_time} — {currentClass.end_time}</span>
              </div>
            )}
          </div>

          {/* Prominent Room Number Badge & Live Countdown */}
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', background: 'rgba(0, 0, 0, 0.25)', padding: '0.85rem 1rem', borderRadius: '14px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <MapPin className="text-indigo-400" size={24} />
              <div>
                <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>Location</div>
                <div className="room-badge-large" style={{ padding: '0.2rem 0.8rem', fontSize: '1.3rem' }}>
                  ROOM {currentClass.room}
                </div>
              </div>
            </div>

            <div className="countdown-container">
              <div className="pulse-dot"></div>
              <div>
                <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>Time Remaining</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#34d399' }}>
                  {formattedCountdown}
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Non-Active States: FREE, LUNCH, BREAK, HOLIDAY, WEEKEND, CANCELLED */
        <div style={{ padding: '1rem 0', textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', padding: '1rem', borderRadius: '50%', background: 'rgba(255, 255, 255, 0.05)', marginBottom: '0.75rem', color: '#a78bfa' }}>
            {status === 'HOLIDAY' ? <Sparkles size={32} /> : <Calendar size={32} />}
          </div>
          <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#f8fafc', marginBottom: '0.35rem' }}>
            {status === 'FREE' && 'No Active Class Right Now'}
            {status === 'LUNCH' && 'Lunch Break'}
            {status === 'BREAK' && 'Recess / Short Break'}
            {status === 'HOLIDAY' && (currentClass.holiday_name || 'Academic Holiday')}
            {status === 'WEEKEND' && 'Weekend — No Classes Scheduled'}
            {status === 'CANCELLED' && 'Current Class Cancelled'}
            {status === 'BEFORE_FIRST_PERIOD' && 'Before First Period'}
            {status === 'AFTER_LAST_PERIOD' && 'Classes Done For Today'}
          </h3>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            {status === 'FREE' && 'You have a free period. Check free rooms or study areas.'}
            {status === 'LUNCH' && 'Enjoy your meal break from 12:40 to 13:40.'}
            {status === 'HOLIDAY' && 'Relax and enjoy your day off.'}
            {status === 'CANCELLED' && `Class ${currentClass.subject || ''} was cancelled for today.`}
            {status === 'BEFORE_FIRST_PERIOD' && 'First class starts at 08:40 AM.'}
            {status === 'AFTER_LAST_PERIOD' && 'All scheduled lectures have concluded.'}
          </p>
        </div>
      )}
    </div>
  );
}
