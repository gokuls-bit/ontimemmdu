import React, { useState, useEffect } from 'react';
import { getFreeRooms } from '../../api/roomApi';
import { DoorOpen, Filter, CheckCircle } from 'lucide-react';

export function FreeRoomFinder({ onSelectRoom }) {
  const [filterType, setFilterType] = useState('');
  const [freeRooms, setFreeRooms] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadFreeRooms() {
      setLoading(true);
      try {
        const data = await getFreeRooms(filterType);
        setFreeRooms(data || []);
      } catch (err) {
        console.error('Error fetching free rooms:', err);
      } finally {
        setLoading(false);
      }
    }
    loadFreeRooms();
  }, [filterType]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Filter Buttons */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <Filter size={14} /> FILTER:
        </span>
        <button
          onClick={() => setFilterType('')}
          style={{
            padding: '0.35rem 0.85rem',
            borderRadius: '9999px',
            fontSize: '0.8rem',
            fontWeight: 700,
            cursor: 'pointer',
            border: filterType === '' ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.12)',
            background: filterType === '' ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255,255,255,0.05)',
            color: filterType === '' ? '#a78bfa' : 'var(--text-secondary)',
          }}
        >
          ALL FREE
        </button>
        <button
          onClick={() => setFilterType('CLASSROOM')}
          style={{
            padding: '0.35rem 0.85rem',
            borderRadius: '9999px',
            fontSize: '0.8rem',
            fontWeight: 700,
            cursor: 'pointer',
            border: filterType === 'CLASSROOM' ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.12)',
            background: filterType === 'CLASSROOM' ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255,255,255,0.05)',
            color: filterType === 'CLASSROOM' ? '#a78bfa' : 'var(--text-secondary)',
          }}
        >
          CLASSROOMS
        </button>
        <button
          onClick={() => setFilterType('LABORATORY')}
          style={{
            padding: '0.35rem 0.85rem',
            borderRadius: '9999px',
            fontSize: '0.8rem',
            fontWeight: 700,
            cursor: 'pointer',
            border: filterType === 'LABORATORY' ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.12)',
            background: filterType === 'LABORATORY' ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255,255,255,0.05)',
            color: filterType === 'LABORATORY' ? '#a78bfa' : 'var(--text-secondary)',
          }}
        >
          LABORATORIES
        </button>
      </div>

      {/* Grid of Free Rooms */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '0.75rem' }}>
        {freeRooms.map((room) => {
          const roomNum = typeof room === 'string' ? room : (room.room_number || room.room);
          const roomType = typeof room === 'object' ? room.room_type : 'CLASSROOM';

          return (
            <button
              key={roomNum}
              onClick={() => onSelectRoom && onSelectRoom(roomNum)}
              className="glass-card"
              style={{
                padding: '0.85rem',
                textAlign: 'center',
                cursor: 'pointer',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                background: 'rgba(16, 185, 129, 0.08)',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ fontSize: '0.7rem', fontWeight: 800, color: '#34d399', textTransform: 'uppercase', marginBottom: '0.2rem' }}>
                ✓ FREE NOW
              </div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc' }}>
                {roomNum}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                {roomType || 'Room'}
              </div>
            </button>
          );
        })}
      </div>

      {freeRooms.length === 0 && !loading && (
        <div className="glass-card" style={{ textAlign: 'center', padding: '2rem' }}>
          <p style={{ color: 'var(--text-secondary)' }}>No free rooms found for the selected filter right now.</p>
        </div>
      )}
    </div>
  );
}
