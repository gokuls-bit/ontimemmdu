import React from 'react';
import { Search, User, MapPin, Clock, BookOpen, ChevronRight, CheckCircle2 } from 'lucide-react';
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
      <div className="glass-card" style={{ padding: '0.85rem 1.1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Search size={20} style={{ color: 'var(--accent-primary)' }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search faculty by name (e.g. Sharma, Verma, Gupta)..."
            style={{
              width: '100%',
              background: 'none',
              border: 'none',
              color: 'var(--text-primary)',
              fontSize: '1rem',
              fontWeight: 600,
              outline: 'none',
            }}
          />
        </div>
      </div>

      {/* Autocomplete Search Results */}
      {searchResults.length > 0 && !selectedTeacherLocation && (
        <div className="glass-card" style={{ padding: '0.5rem' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', padding: '0.5rem 0.75rem' }}>
            Faculty Members Found
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
                padding: '0.8rem 0.85rem',
                borderRadius: '10px',
                background: 'none',
                border: 'none',
                color: 'var(--text-primary)',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'var(--accent-primary-gradient)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 800, fontSize: '0.9rem' }}>
                  {(teacher.name || teacher.first_name || 'F').charAt(0)}
                </div>
                <div>
                  <div style={{ fontWeight: 800, fontSize: '0.95rem' }}>{teacher.name || `${teacher.first_name} ${teacher.last_name}`}</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{teacher.designation || 'Faculty'} • CSE</div>
                </div>
              </div>
              <span style={{ fontSize: '0.8rem', color: 'var(--accent-primary)', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                Locate <ChevronRight size={14} />
              </span>
            </button>
          ))}
        </div>
      )}

      {/* Teacher Location Card */}
      {selectedTeacherLocation && (
        <div className="glass-card" style={{ borderLeft: selectedTeacherLocation.status === 'TEACHING' ? '4px solid var(--status-active)' : '4px solid var(--status-free)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: 'var(--accent-primary-gradient)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 800, fontSize: '1.2rem', boxShadow: '0 4px 12px var(--accent-glow)' }}>
                {(selectedTeacherLocation.teacher || 'F').charAt(0)}
              </div>
              <div>
                <span style={{ fontSize: '0.72rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                  FACULTY PROFILE & LIVE LOCATION
                </span>
                <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                  {selectedTeacherLocation.teacher}
                </h2>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {selectedTeacherLocation.designation} • Department of {selectedTeacherLocation.department || 'CSE'}
                </div>
              </div>
            </div>
            <StatusBadge status={selectedTeacherLocation.status === 'TEACHING' ? 'ACTIVE_CLASS' : 'FREE'} />
          </div>

          {selectedTeacherLocation.status === 'TEACHING' ? (
            <div style={{ background: 'var(--status-active-bg)', padding: '1rem 1.1rem', borderRadius: '14px', border: '1px solid rgba(139, 92, 246, 0.3)', marginBottom: '1.25rem' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--status-active)', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                CURRENTLY TEACHING IN
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.6rem' }}>
                <div className="room-badge-large" style={{ fontSize: '1.2rem', padding: '0.35rem 0.9rem' }}>
                  <MapPin size={18} /> ROOM {selectedTeacherLocation.room}
                </div>
              </div>

              <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                {selectedTeacherLocation.subject}
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                Section: <strong style={{ color: 'var(--text-primary)' }}>{selectedTeacherLocation.section}</strong> {selectedTeacherLocation.group ? `(Group ${selectedTeacherLocation.group})` : ''} | Time: <strong>{selectedTeacherLocation.start_time} — {selectedTeacherLocation.end_time}</strong>
              </div>
            </div>
          ) : (
            <div style={{ background: 'var(--status-free-bg)', padding: '1rem 1.1rem', borderRadius: '14px', border: '1px solid rgba(16, 185, 129, 0.3)', marginBottom: '1.25rem', color: 'var(--status-free)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CheckCircle2 size={20} /> Faculty is currently free / in staff room right now.
            </div>
          )}

          {/* Teacher Today's Schedule Table */}
          {selectedTeacherSchedule && selectedTeacherSchedule.schedule && (
            <div>
              <h4 style={{ fontSize: '0.78rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
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
                      padding: '0.7rem 0.9rem',
                      borderRadius: '10px',
                      background: 'var(--bg-input)',
                      border: '1px solid var(--glass-border)',
                      fontSize: '0.88rem',
                    }}
                  >
                    <div>
                      <span style={{ color: 'var(--accent-primary)', fontWeight: 800, marginRight: '0.5rem' }}>P{entry.period}</span>
                      <strong style={{ color: 'var(--text-primary)' }}>{entry.subject || 'Free'}</strong>
                      {entry.section && <span style={{ color: 'var(--text-muted)', marginLeft: '0.5rem' }}>({entry.section})</span>}
                    </div>
                    {entry.room && (
                      <span style={{ color: 'var(--status-active)', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <MapPin size={14} /> RM {entry.room}
                      </span>
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
