import React, { useState, useEffect } from 'react';
import { getStudentSchedule } from '../api/studentApi';
import { TodayScheduleTimeline } from '../components/student/TodayScheduleTimeline';
import { Calendar as CalendarIcon, Filter, Layers } from 'lucide-react';

export function TimetablePage({ context }) {
  const [selectedDay, setSelectedDay] = useState('MON');
  const [order, setOrder] = useState('asc');
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(false);

  const days = [
    { code: 'MON', label: 'Mon' },
    { code: 'TUE', label: 'Tue' },
    { code: 'WED', label: 'Wed' },
    { code: 'THU', label: 'Thu' },
    { code: 'FRI', label: 'Fri' },
    { code: 'SAT', label: 'Sat' },
  ];

  useEffect(() => {
    if (!context) return;
    async function loadSchedule() {
      setLoading(true);
      try {
        const res = await getStudentSchedule(context.semester, context.section, context.group, selectedDay, order);
        setSchedule(res?.schedule || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadSchedule();
  }, [context, selectedDay, order]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'var(--accent-primary-gradient)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <CalendarIcon size={20} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                Weekly Timetable Matrix
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {context?.semester}th Sem • Section {context?.section} {context?.group ? `(Group ${context.group})` : ''}
              </p>
            </div>
          </div>
        </div>

        {/* Day Selector Tabs */}
        <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'space-between' }}>
          {days.map((d) => (
            <button
              key={d.code}
              onClick={() => setSelectedDay(d.code)}
              style={{
                flex: 1,
                padding: '0.6rem 0.2rem',
                borderRadius: '10px',
                fontWeight: 800,
                fontSize: '0.82rem',
                cursor: 'pointer',
                border: selectedDay === d.code ? '1px solid var(--accent-primary)' : '1px solid var(--glass-border)',
                background: selectedDay === d.code ? 'var(--status-active-bg)' : 'var(--bg-input)',
                color: selectedDay === d.code ? 'var(--accent-primary)' : 'var(--text-secondary)',
                transition: 'all 0.2s ease',
              }}
            >
              {d.label}
            </button>
          ))}
        </div>
      </div>

      <TodayScheduleTimeline schedule={schedule} order={order} onOrderChange={setOrder} />
    </div>
  );
}
