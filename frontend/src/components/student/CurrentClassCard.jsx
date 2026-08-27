import React from 'react';
import { StatusBadge } from '../common/StatusBadge';
import { MapPin, User, Clock, Calendar, Sparkles, Coffee, ArrowRight, Compass } from 'lucide-react';
import { useServerClock } from '../../hooks/useServerClock';

export function CurrentClassCard({ currentClass, serverTime, onInspectRoom }) {
  const { formattedCountdown, secondsRemaining } = useServerClock(serverTime, currentClass?.minutes_remaining);

  if (!currentClass) return null;

  const status = currentClass.status || 'FREE';
  const isClassActive = status === 'ACTIVE_CLASS';

  // Calculate lecture progress percentage if active class
  let progressPercent = 50;
  if (isClassActive && currentClass.start_time && currentClass.end_time) {
    const totalMinutes = 50; // standard period duration is 50 mins
    const remainingMinutes = currentClass.minutes_remaining ?? 25;
    const elapsedMinutes = Math.max(0, Math.min(totalMinutes, totalMinutes - remainingMinutes));
    progressPercent = Math.round((elapsedMinutes / totalMinutes) * 100);
  }

  return (
    <div
      className="glass-card"
      style={{
        position: 'relative',
        overflow: 'hidden',
        border: isClassActive
          ? '1px solid rgba(99, 102, 241, 0.4)'
          : '1px solid var(--glass-border)',
        boxShadow: isClassActive
          ? '0 12px 36px var(--accent-glow)'
          : 'var(--glass-shadow)',
        background: isClassActive
          ? 'linear-gradient(145deg, var(--bg-card-solid) 0%, rgba(99, 102, 241, 0.12) 100%)'
          : 'var(--bg-card)',
      }}
    >
      {/* Top Banner & Period Badge */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.72rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)' }}>
            RIGHT NOW
          </span>
          <StatusBadge status={status} />
        </div>
        {currentClass.period && (
          <span
            style={{
              fontSize: '0.78rem',
              fontWeight: 800,
              color: 'var(--status-active)',
              background: 'var(--status-active-bg)',
              padding: '0.25rem 0.65rem',
              borderRadius: '8px',
              border: '1px solid rgba(139, 92, 246, 0.25)',
            }}
          >
            Period {currentClass.period}
          </span>
        )}
      </div>

      {/* Main Content View based on State */}
      {isClassActive ? (
        <div>
          {/* Subject Header */}
          <div style={{ marginBottom: '0.75rem' }}>
            <h2 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.35rem', lineHeight: 1.2 }}>
              {currentClass.subject_name || currentClass.subject}
            </h2>
            {currentClass.subject_code && (
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', background: 'var(--bg-input)', padding: '0.2rem 0.5rem', borderRadius: '6px' }}>
                {currentClass.subject_code}
              </span>
            )}
          </div>

          {/* Teacher & Time Info Row */}
          <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '1.25rem', marginBottom: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
            {currentClass.teacher && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <div style={{ width: '26px', height: '26px', borderRadius: '50%', background: 'var(--accent-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-primary)' }}>
                  <User size={15} />
                </div>
                <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{currentClass.teacher}</span>
              </div>
            )}
            {currentClass.start_time && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Clock size={16} style={{ color: 'var(--accent-primary)' }} />
                <span style={{ fontWeight: 600 }}>{currentClass.start_time} — {currentClass.end_time}</span>
              </div>
            )}
          </div>

          {/* Live Progress Bar */}
          <div style={{ marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
              <span>Lecture Progress</span>
              <span>{progressPercent}% Complete</span>
            </div>
            <div className="progress-bar-track">
              <div className="progress-bar-fill" style={{ width: `${progressPercent}%` }}></div>
            </div>
          </div>

          {/* Location & Live Countdown Container */}
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', background: 'var(--bg-input)', padding: '0.85rem 1.1rem', borderRadius: '16px', border: '1px solid var(--glass-border)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div className="room-badge-large">
                <MapPin size={20} /> ROOM {currentClass.room}
              </div>
              {onInspectRoom && (
                <button
                  onClick={() => onInspectRoom(currentClass.room)}
                  style={{
                    background: 'var(--status-active-bg)',
                    border: '1px solid rgba(139, 92, 246, 0.3)',
                    color: 'var(--status-active)',
                    padding: '0.4rem 0.75rem',
                    borderRadius: '10px',
                    fontSize: '0.8rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.3rem',
                  }}
                >
                  Locate <ArrowRight size={14} />
                </button>
              )}
            </div>

            <div className="countdown-container">
              <div className="pulse-dot"></div>
              <div>
                <div style={{ fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>Time Remaining</div>
                <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--status-free)' }}>
                  {formattedCountdown}
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Human Off-Hours & Free States */
        <div style={{ padding: '1.25rem 0.5rem', textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', padding: '1rem', borderRadius: '20px', background: 'var(--status-active-bg)', marginBottom: '0.85rem', color: 'var(--accent-primary)' }}>
            {status === 'HOLIDAY' ? <Sparkles size={32} /> : status === 'LUNCH' ? <Coffee size={32} /> : <Calendar size={32} />}
          </div>
          <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>
            {status === 'FREE' && "You're Free Right Now! ☕"}
            {status === 'LUNCH' && 'Lunch Break Time! 🍱'}
            {status === 'BREAK' && 'Short Recess Break 🥤'}
            {status === 'HOLIDAY' && (currentClass.holiday_name || 'Academic Holiday 🎉')}
            {status === 'WEEKEND' && 'Happy Weekend! 🌴'}
            {status === 'CANCELLED' && 'Class Cancelled Today ⚠️'}
            {status === 'BEFORE_FIRST_PERIOD' && 'Morning Warmup 🌅'}
            {status === 'AFTER_LAST_PERIOD' && 'Classes Concluded For Today! 🎉'}
          </h3>
          <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)', maxWidth: '480px', margin: '0 auto' }}>
            {status === 'FREE' && 'No scheduled lecture during this period. Take a break or check available study rooms.'}
            {status === 'LUNCH' && 'Refuel and relax! Lunch recess runs from 12:40 PM to 1:40 PM.'}
            {status === 'HOLIDAY' && 'Enjoy your well-deserved day off.'}
            {status === 'CANCELLED' && `Class ${currentClass.subject || ''} was cancelled for today.`}
            {status === 'BEFORE_FIRST_PERIOD' && 'Your first period starts at 8:40 AM. Grab a seats early!'}
            {status === 'AFTER_LAST_PERIOD' && 'All lectures (8:40 AM — 3:40 PM) are complete. Have a great evening!'}
          </p>
        </div>
      )}
    </div>
  );
}
