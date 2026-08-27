import React from 'react';
import { Search, MapPin, User, Clock, CheckCircle, XCircle, Building2, Layers, Users } from 'lucide-react';
import { StatusBadge } from '../common/StatusBadge';

export function RoomLocator({
  searchQuery,
  setSearchQuery,
  searchResults,
  selectedRoomStatus,
  inspectRoom,
  loading,
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Search Box */}
      <div className="glass-card" style={{ padding: '0.85rem 1.1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Search size={20} style={{ color: 'var(--accent-primary)' }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Type room number (e.g. 302, 405, Lab 1)..."
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

      {/* Search Results Autocomplete List */}
      {searchResults.length > 0 && !selectedRoomStatus && (
        <div className="glass-card" style={{ padding: '0.5rem' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', padding: '0.5rem 0.75rem' }}>
            Matching Campus Classrooms
          </div>
          {searchResults.map((room) => (
            <button
              key={room.room_number || room}
              onClick={() => inspectRoom(room.room_number || room)}
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
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'var(--status-active-bg)', color: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyCenter: 'center', flexShrink: 0 }}>
                  <MapPin size={18} />
                </div>
                <span style={{ fontWeight: 800, fontSize: '1rem' }}>ROOM {room.room_number || room}</span>
              </div>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                {room.room_type || 'Classroom'} • {room.capacity || 60} Seats
              </span>
            </button>
          ))}
        </div>
      )}

      {/* Room Detail Card */}
      {selectedRoomStatus && (
        <div className="glass-card" style={{ borderLeft: selectedRoomStatus.status === 'FREE' ? '4px solid var(--status-free)' : '4px solid var(--status-occupied)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <span style={{ fontSize: '0.72rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                ROOM INFORMATION
              </span>
              <h2 style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                ROOM {selectedRoomStatus.room}
              </h2>
            </div>
            <StatusBadge status={selectedRoomStatus.status} />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem', background: 'var(--bg-input)', padding: '1rem', borderRadius: '14px', marginBottom: '1rem', fontSize: '0.88rem', border: '1px solid var(--glass-border)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Building2 size={16} style={{ color: 'var(--accent-primary)' }} />
              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.7rem' }}>Building</span>
                <strong style={{ color: 'var(--text-primary)' }}>{selectedRoomStatus.building || 'Main CSE Block'}</strong>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Layers size={16} style={{ color: 'var(--accent-primary)' }} />
              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.7rem' }}>Floor</span>
                <strong style={{ color: 'var(--text-primary)' }}>Floor {selectedRoomStatus.floor ?? 3}</strong>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <MapPin size={16} style={{ color: 'var(--accent-primary)' }} />
              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.7rem' }}>Type</span>
                <strong style={{ color: 'var(--text-primary)' }}>{selectedRoomStatus.room_type || 'Classroom'}</strong>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Users size={16} style={{ color: 'var(--accent-primary)' }} />
              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.7rem' }}>Capacity</span>
                <strong style={{ color: 'var(--text-primary)' }}>{selectedRoomStatus.capacity} Seats</strong>
              </div>
            </div>
          </div>

          {selectedRoomStatus.status === 'OCCUPIED' && selectedRoomStatus.current_class && (
            <div style={{ padding: '0.95rem 1.1rem', borderRadius: '14px', background: 'var(--status-occupied-bg)', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--status-occupied)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                CURRENT LECTURE IN SESSION
              </div>
              <h4 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                {selectedRoomStatus.current_class.subject}
              </h4>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                Faculty: <strong style={{ color: 'var(--text-primary)' }}>{selectedRoomStatus.current_class.teacher}</strong> | Section: <strong>{selectedRoomStatus.current_class.section}</strong>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
