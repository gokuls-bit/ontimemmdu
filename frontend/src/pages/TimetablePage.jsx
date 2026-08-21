import React, { useState, useEffect } from 'react';
import { getStudentSchedule } from '../api/studentApi';
import { TodayScheduleTimeline } from '../components/student/TodayScheduleTimeline';
import { Calendar as CalendarIcon, Filter } from 'lucide-react';

export function TimetablePage({ context }) {
  const [selectedDay, setSelectedDay] = useState('MON');
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(false);

  const days = [
    { code: 'MON', label: 'Mon' },
    { code: 'TUE', label: 'Tue' },
    { code: 'WED', label: 'Wed' },
    { code: 'THU', label: 'Thu' },
    { code: 'FRI', label: 'Fri' },
  ];

  useEffect(() => {
    if (!context) return;
    async function loadSchedule() {
      setLoading(true);
      try {
        const res = await getStudentSchedule(context.semester, context.section, context.group, selectedDay);
        setSchedule(res?.schedule || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadSchedule();
  }, [context, selectedDay]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
          <CalendarIcon className="text-indigo-400" size={22} />
          <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc' }}>
            Weekly Timetable Schedule
          </h3>
        </div>

        {/* Day Selector Tabs */}
        <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'space-between' }}>
          {days.map((d) => (
            <button
              key={d.code}
              onClick={() => setSelectedDay(d.code)}
              style={{
                flex: 1,
                padding: '0.5rem 0.2rem',
                borderRadius: '8px',
                fontWeight: 700,
                fontSize: '0.85rem',
                cursor: 'pointer',
                border: selectedDay === d.code ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.08)',
                background: selectedDay === d.code ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255,255,255,0.04)',
                color: selectedDay === d.code ? '#a78bfa' : 'var(--text-secondary)',
              }}
            >
              {d.label}
            </button>
          ))}
        </div>
      </div>

      <TodayScheduleTimeline schedule={schedule} />
    </div>
  );
}
