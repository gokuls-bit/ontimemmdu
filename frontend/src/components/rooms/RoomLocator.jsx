import React from 'react';
import { Search, MapPin, User, Clock, CheckCircle, XCircle } from 'lucide-react';
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
      <div className="glass-card" style={{ padding: '0.85rem 1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Search size={20} className="text-indigo-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search room number (e.g. 357, Lab-1)..."
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

      {/* Search Results Autocomplete List */}
      {searchResults.length > 0 && !selectedRoomStatus && (
        <div className="glass-card" style={{ padding: '0.5rem' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', padding: '0.5rem 0.75rem' }}>
            Matching Rooms
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
                <MapPin size={18} className="text-indigo-400" />
                <span style={{ fontWeight: 700 }}>ROOM {room.room_number || room}</span>
              </div>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                {room.room_type || 'CLASSROOM'} • Cap: {room.capacity || 60}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* Room Detail Card */}
      {selectedRoomStatus && (
        <div className="glass-card" style={{ borderLeft: selectedRoomStatus.status === 'FREE' ? '4px solid #10b981' : '4px solid #f59e0b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <span style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                ROOM DETAILS
              </span>
              <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc' }}>
                ROOM {selectedRoomStatus.room}
              </h2>
            </div>
            <StatusBadge status={selectedRoomStatus.status} />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', background: 'rgba(0,0,0,0.25)', padding: '0.85rem', borderRadius: '12px', marginBottom: '1rem', fontSize: '0.85rem' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Building:</span>{' '}
              <strong style={{ color: '#fff' }}>{selectedRoomStatus.building || 'Main CSE Block'}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Floor:</span>{' '}
              <strong style={{ color: '#fff' }}>Floor {selectedRoomStatus.floor ?? 3}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Type:</span>{' '}
              <strong style={{ color: '#fff' }}>{selectedRoomStatus.room_type || 'Classroom'}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Capacity:</span>{' '}
              <strong style={{ color: '#fff' }}>{selectedRoomStatus.capacity} Seats</strong>
            </div>
          </div>

          {selectedRoomStatus.status === 'OCCUPIED' && selectedRoomStatus.current_class && (
            <div style={{ marginBottom: '1rem', padding: '0.85rem', borderRadius: '12px', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.25)' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#fbbf24', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                CURRENTLY IN SESSION
              </div>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>
                {selectedRoomStatus.current_class.subject}
              </h4>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                Teacher: <strong>{selectedRoomStatus.current_class.teacher}</strong> | Section: <strong>{selectedRoomStatus.current_class.section}</strong>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
