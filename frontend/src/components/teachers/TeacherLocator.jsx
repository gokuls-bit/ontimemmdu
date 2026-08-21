import React from 'react';
import { Search, User, MapPin, Clock, BookOpen } from 'lucide-react';
import { StatusBadge } from '../common/StatusBadge';

export function TeacherLocator({
  searchQuery,
  setSearchQuery,
  searchResults,
  selectedTeacherLocation,
  selectedTeacherSchedule,
  inspectTeacher,
  loading,
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Search Input */}
      <div className="glass-card" style={{ padding: '0.85rem 1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Search size={20} className="text-indigo-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search teacher name (e.g. Turing, Sharma)..."
            style={{
              width: '100%',
              background: 'none',
              border: 'none',
              color: '#fff',
              fontSize: '1rem',
              outline: 'none',
            }}
          />
        </div>
      </div>

      {/* Autocomplete Search Results */}
      {searchResults.length > 0 && !selectedTeacherLocation && (
        <div className="glass-card" style={{ padding: '0.5rem' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', padding: '0.5rem 0.75rem' }}>
            Matching Faculty Members
          </div>
          {searchResults.map((teacher) => (
            <button
              key={teacher.employee_id || teacher.id}
              onClick={() => inspectTeacher(teacher.employee_id || teacher.name)}
              style={{
                width: '100%',
                display: 'flex',
                justify: 'space-between',
                alignItems: 'center',
                padding: '0.75rem',
                borderRadius: '8px',
                background: 'none',
                border: 'none',
                color: '#fff',
                cursor: 'pointer',
                textAlign: 'left',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <User size={18} className="text-indigo-400" />
                <div>
                  <div style={{ fontWeight: 700 }}>{teacher.name || `${teacher.first_name} ${teacher.last_name}`}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{teacher.designation || 'Faculty'}</div>
                </div>
              </div>
              <span style={{ fontSize: '0.8rem', color: '#a78bfa', fontWeight: 600 }}>Inspect →</span>
            </button>
          ))}
        </div>
      )}

      {/* Teacher Location Card */}
      {selectedTeacherLocation && (
        <div className="glass-card" style={{ borderLeft: selectedTeacherLocation.status === 'TEACHING' ? '4px solid #8b5cf6' : '4px solid #10b981' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <span style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                FACULTY LOCATION
              </span>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f8fafc' }}>
                {selectedTeacherLocation.teacher}
              </h2>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                {selectedTeacherLocation.designation} • Dept of {selectedTeacherLocation.department || 'CSE'}
              </div>
            </div>
            <StatusBadge status={selectedTeacherLocation.status === 'TEACHING' ? 'ACTIVE_CLASS' : 'FREE'} />
          </div>

          {selectedTeacherLocation.status === 'TEACHING' ? (
            <div style={{ background: 'rgba(139, 92, 246, 0.1)', padding: '1rem', borderRadius: '14px', border: '1px solid rgba(139, 92, 246, 0.25)', marginBottom: '1rem' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#c084fc', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                CURRENTLY TEACHING IN
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <MapPin className="text-indigo-400" size={24} />
                <span className="room-badge-large" style={{ fontSize: '1.25rem', padding: '0.2rem 0.75rem' }}>
                  ROOM {selectedTeacherLocation.room}
                </span>
              </div>

              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff' }}>
                {selectedTeacherLocation.subject}
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                Section: <strong>{selectedTeacherLocation.section}</strong> {selectedTeacherLocation.group ? `(Group ${selectedTeacherLocation.group})` : ''} | Time: <strong>{selectedTeacherLocation.start_time} — {selectedTeacherLocation.end_time}</strong>
              </div>
            </div>
          ) : (
            <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '1rem', borderRadius: '14px', border: '1px solid rgba(16, 185, 129, 0.25)', marginBottom: '1rem', color: '#34d399' }}>
              ✓ Faculty is currently free / not teaching any scheduled class right now.
            </div>
          )}

          {/* Teacher Today's Schedule Table */}
          {selectedTeacherSchedule && selectedTeacherSchedule.schedule && (
            <div>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                TODAY'S TEACHING SCHEDULE
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {selectedTeacherSchedule.schedule.map((entry, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      justify: 'space-between',
                      alignItems: 'center',
                      padding: '0.65rem 0.85rem',
                      borderRadius: '8px',
                      background: 'rgba(0, 0, 0, 0.2)',
                      fontSize: '0.85rem',
                    }}
                  >
                    <div>
                      <span style={{ color: '#a78bfa', fontWeight: 700, marginRight: '0.5rem' }}>P{entry.period}</span>
                      <strong style={{ color: '#fff' }}>{entry.subject || 'Free'}</strong>
                      {entry.section && <span style={{ color: 'var(--text-muted)', marginLeft: '0.5rem' }}>({entry.section})</span>}
                    </div>
                    {entry.room && (
                      <span style={{ color: '#c084fc', fontWeight: 700 }}>ROOM {entry.room}</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
