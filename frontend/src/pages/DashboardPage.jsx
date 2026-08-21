import React from 'react';
import { CurrentClassCard } from '../components/student/CurrentClassCard';
import { NextClassCard } from '../components/student/NextClassCard';
import { RoomTransitionCard } from '../components/student/RoomTransitionCard';
import { NextRoomOccupancyCard } from '../components/student/NextRoomOccupancyCard';
import { TodayScheduleTimeline } from '../components/student/TodayScheduleTimeline';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ErrorNotice } from '../components/common/ErrorNotice';
import { Calendar, DoorOpen, Users, FileSpreadsheet, RefreshCw } from 'lucide-react';

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

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Quick Action Navigation Buttons */}
      <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', paddingBottom: '0.25rem' }}>
        <button
          onClick={() => onNavigateTab('timetable')}
          style={{
            background: 'rgba(99, 102, 241, 0.12)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            color: '#a78bfa',
            padding: '0.5rem 0.85rem',
            borderRadius: '10px',
            fontSize: '0.8rem',
            fontWeight: 700,
            whiteSpace: 'nowrap',
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            cursor: 'pointer',
          }}
        >
          <Calendar size={14} /> Timetable
        </button>

        <button
          onClick={() => onNavigateTab('rooms')}
          style={{
            background: 'rgba(16, 185, 129, 0.12)',
            border: '1px solid rgba(16, 185, 129, 0.25)',
            color: '#34d399',
            padding: '0.5rem 0.85rem',
            borderRadius: '10px',
            fontSize: '0.8rem',
            fontWeight: 700,
            whiteSpace: 'nowrap',
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            cursor: 'pointer',
          }}
        >
          <DoorOpen size={14} /> Free Rooms
        </button>

        <button
          onClick={() => onNavigateTab('teachers')}
          style={{
            background: 'rgba(56, 189, 248, 0.12)',
            border: '1px solid rgba(56, 189, 248, 0.25)',
            color: '#38bdf8',
            padding: '0.5rem 0.85rem',
            borderRadius: '10px',
            fontSize: '0.8rem',
            fontWeight: 700,
            whiteSpace: 'nowrap',
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            cursor: 'pointer',
          }}
        >
          <Users size={14} /> Find Teacher
        </button>
      </div>

      {/* 1. Visually Dominant Current Class Card */}
      <CurrentClassCard currentClass={currentClass} serverTime={state.server_time} />

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
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#f8fafc' }}>
            Today's Timetable ({state.day_name || 'Today'})
          </h3>
          <button
            onClick={() => onNavigateTab('timetable')}
            style={{ background: 'none', border: 'none', color: '#a78bfa', fontSize: '0.85rem', fontWeight: 700, cursor: 'pointer' }}
          >
            View Full →
          </button>
        </div>
        <TodayScheduleTimeline schedule={todaySchedule} />
      </div>
    </div>
  );
}
