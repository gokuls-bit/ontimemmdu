import React, { useState } from 'react';
import { StatusBadge } from '../common/StatusBadge';
import { Clock, MapPin, User, ArrowDownUp, LayoutGrid, List, BookOpen, Beaker, CheckCircle2 } from 'lucide-react';

export function TodayScheduleTimeline({ schedule, order = 'asc', onOrderChange }) {
  const [layoutOrientation, setLayoutOrientation] = useState('vertical');
  const [internalOrder, setInternalOrder] = useState(order);

  const currentOrder = onOrderChange ? order : internalOrder;

  const handleToggleOrder = () => {
    const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
    if (onOrderChange) {
      onOrderChange(newOrder);
    } else {
      setInternalOrder(newOrder);
    }
  };

  if (!schedule || schedule.length === 0) {
    return (
      <div className="glass-card" style={{ textAlign: 'center', padding: '2rem' }}>
        <p style={{ color: 'var(--text-secondary)' }}>No timetable entries scheduled for today.</p>
      </div>
    );
  }

  // Ensure items are ordered according to selected orientation if not handled by API
  const displayedSchedule = [...schedule].sort((a, b) => {
    const p1 = a.period || 0;
    const p2 = b.period || 0;
    return currentOrder === 'asc' ? p1 - p2 : p2 - p1;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {/* Orientation & View Controls */}
      <div
        className="glass-card"
        style={{
          padding: '0.65rem 0.9rem',
          display: 'flex',
          justify: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.5rem',
          fontSize: '0.8rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--accent-primary)', fontWeight: 800 }}>
          <Clock size={15} />
          <span>Lectures (8:40 AM — 3:40 PM)</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          {/* Order Orientation Toggle Button */}
          <button
            onClick={handleToggleOrder}
            title="Change lecture order"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: '0.35rem 0.65rem',
              borderRadius: '8px',
              border: '1px solid var(--glass-border)',
              background: 'var(--bg-input)',
              color: 'var(--text-primary)',
              fontWeight: 700,
              fontSize: '0.75rem',
              cursor: 'pointer',
            }}
          >
            <ArrowDownUp size={13} style={{ color: 'var(--accent-primary)' }} />
            <span>{currentOrder === 'asc' ? '8:40 AM → 3:40 PM' : '3:40 PM → 8:40 AM'}</span>
          </button>

          {/* Layout Orientation Toggle */}
          <button
            onClick={() => setLayoutOrientation(layoutOrientation === 'vertical' ? 'horizontal' : 'vertical')}
            title="Toggle Layout Orientation"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.25rem',
              padding: '0.35rem 0.55rem',
              borderRadius: '8px',
              border: '1px solid var(--glass-border)',
              background: 'var(--bg-input)',
              color: 'var(--text-secondary)',
              fontWeight: 600,
              fontSize: '0.75rem',
              cursor: 'pointer',
            }}
          >
            {layoutOrientation === 'vertical' ? <LayoutGrid size={13} /> : <List size={13} />}
            <span>{layoutOrientation === 'vertical' ? 'Grid' : 'List'}</span>
          </button>
        </div>
      </div>

      {/* Lectures Schedule Container */}
      <div
        style={
          layoutOrientation === 'horizontal'
            ? {
                display: 'flex',
                gap: '0.75rem',
                overflowX: 'auto',
                paddingBottom: '0.5rem',
              }
            : {
                display: 'flex',
                flexDirection: 'column',
                gap: '0.75rem',
              }
        }
      >
        {displayedSchedule.map((entry, idx) => {
          const isCurrent = entry.status === 'CURRENT' || entry.status === 'ACTIVE_CLASS';
          const isCompleted = entry.status === 'COMPLETED';
          const isFree = entry.status === 'FREE';
          const isCancelled = entry.status === 'CANCELLED';
          const isLab = entry.subject?.toLowerCase().includes('lab') || entry.subject_code?.toLowerCase().includes('lab');

          return (
            <div
              key={idx}
              className="glass-card"
              style={{
                padding: '0.95rem 1.1rem',
                minWidth: layoutOrientation === 'horizontal' ? '250px' : 'auto',
                flexShrink: layoutOrientation === 'horizontal' ? 0 : 1,
                opacity: isCompleted ? 0.7 : 1,
                borderLeft: isCurrent
                  ? '4px solid var(--status-active)'
                  : isCompleted
                  ? '4px solid var(--text-muted)'
                  : isFree
                  ? '4px solid var(--status-free)'
                  : isCancelled
                  ? '4px solid var(--status-cancelled)'
                  : '4px solid var(--accent-primary)',
                background: isCurrent ? 'var(--status-active-bg)' : 'var(--bg-card)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.45rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700 }}>
                  <Clock size={13} />
                  <span>Period {entry.period} ({entry.start_time} — {entry.end_time})</span>
                </div>
                <StatusBadge status={entry.status} />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    {isLab ? <Beaker size={16} style={{ color: 'var(--accent-primary)' }} /> : <BookOpen size={16} style={{ color: 'var(--accent-primary)' }} />}
                    <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: isCancelled ? 'var(--status-cancelled)' : 'var(--text-primary)' }}>
                      {isCancelled ? `[CANCELLED] ${entry.subject || ''}` : (entry.subject || 'Free Period')}
                    </h4>
                  </div>

                  {entry.teacher && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.3rem' }}>
                      <User size={14} style={{ color: 'var(--accent-primary)' }} />
                      <span style={{ fontWeight: 600 }}>{entry.teacher}</span>
                    </div>
                  )}
                </div>

                {entry.room && (
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--status-active)', fontWeight: 800, fontSize: '0.95rem' }}>
                      <MapPin size={15} />
                      <span>RM {entry.room}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
