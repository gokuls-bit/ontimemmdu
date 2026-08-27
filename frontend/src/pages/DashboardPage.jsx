import React from 'react';
import { CurrentClassCard } from '../components/student/CurrentClassCard';
import { NextClassCard } from '../components/student/NextClassCard';
import { RoomTransitionCard } from '../components/student/RoomTransitionCard';
import { NextRoomOccupancyCard } from '../components/student/NextRoomOccupancyCard';
import { TodayScheduleTimeline } from '../components/student/TodayScheduleTimeline';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ErrorNotice } from '../components/common/ErrorNotice';
import { Calendar, DoorOpen, Users, ArrowRight, Sun, Sparkles, Footprints } from 'lucide-react';

export function DashboardPage({
  state,
  loading,
  error,
  onRefresh,
  onNavigateTab,
  onInspectRoom,
}) {
  if (loading && !state) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <LoadingSkeleton />
        <LoadingSkeleton />
      </div>
    );
  }

  if (error && !state) {
    return <ErrorNotice message={error.message} onRetry={onRefresh} />;
  }

  if (!state) return null;

  const currentClass = state.current_class;
  const nextClass = state.next_class;
  const todaySchedule = state.today_schedule || [];

  // Determine greeting based on current time
  const currentHour = new Date().getHours();
  let timeGreeting = 'Good day! ☀️';
  if (currentHour < 12) timeGreeting = 'Good morning! 🌅';
  else if (currentHour < 17) timeGreeting = 'Good afternoon! ☀️';
  else timeGreeting = 'Good evening! 🌙';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Personalized Human Greeting Header */}
      <div className="glass-card" style={{ background: 'var(--accent-primary-gradient)', color: '#ffffff', border: 'none' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', background: 'rgba(255, 255, 255, 0.2)', padding: '0.2rem 0.6rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
              <Sparkles size={13} /> {state.day_name || 'Today'} Overview
            </div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, lineHeight: 1.2, color: '#ffffff' }}>
              {timeGreeting}
            </h2>
            <p style={{ fontSize: '0.88rem', opacity: 0.9, marginTop: '0.2rem', fontWeight: 500 }}>
              Here is your live campus timetable and room schedule.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
            <button
              onClick={() => onNavigateTab('timetable')}
              style={{
                background: 'rgba(255, 255, 255, 0.2)',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                color: '#ffffff',
                padding: '0.45rem 0.75rem',
                borderRadius: '10px',
                fontSize: '0.8rem',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                cursor: 'pointer',
              }}
            >
              <Calendar size={14} /> Schedule
            </button>

            <button
              onClick={() => onNavigateTab('rooms')}
              style={{
                background: 'rgba(255, 255, 255, 0.2)',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                color: '#ffffff',
                padding: '0.45rem 0.75rem',
                borderRadius: '10px',
                fontSize: '0.8rem',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                cursor: 'pointer',
              }}
            >
              <DoorOpen size={14} /> Free Rooms
            </button>
          </div>
        </div>
      </div>

      {/* 1. Visually Dominant Current Class Card */}
      <CurrentClassCard currentClass={currentClass} serverTime={state.server_time} onInspectRoom={onInspectRoom} />

      {/* 2. Room Transition Experience (If next class exists) */}
      {currentClass?.room && nextClass?.room && (
        <RoomTransitionCard
          currentRoom={currentClass.room}
          nextRoom={nextClass.room}
          leaveTime={currentClass.end_time}
        />
      )}

      {/* 3. Next Room Occupancy Live Card */}
      {nextClass?.room && <NextRoomOccupancyCard nextRoom={nextClass.room} />}

      {/* 4. Next Class Card */}
      <NextClassCard nextClass={nextClass} onGoToRoom={onInspectRoom} />

      {/* 5. Today's Timetable Section */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', padding: '0 0.25rem' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            Today's Schedule ({state.day_name || 'Today'})
          </h3>
          <button
            onClick={() => onNavigateTab('timetable')}
            style={{ background: 'none', border: 'none', color: 'var(--accent-primary)', fontSize: '0.85rem', fontWeight: 800, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
          >
            Full Week <ArrowRight size={14} />
          </button>
        </div>
        <TodayScheduleTimeline schedule={todaySchedule} />
      </div>
    </div>
  );
}
