import React, { useState, useEffect } from 'react';
import { getFreeRooms } from '../../api/roomApi';
import { DoorOpen, Filter, CheckCircle2, Search } from 'lucide-react';

export function FreeRoomFinder({ onSelectRoom }) {
  const [filterType, setFilterType] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
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

  const filteredRooms = freeRooms.filter((room) => {
    const roomNum = String(typeof room === 'string' ? room : (room.room_number || room.room));
    return roomNum.toLowerCase().includes(searchTerm.toLowerCase());
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Search Input & Filter Pills */}
      <div className="glass-card" style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        <div style={{ position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search room number (e.g. 302, 405)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem 1rem 0.75rem 2.8rem',
              borderRadius: '12px',
              background: 'var(--bg-input)',
              border: '1px solid var(--glass-border)',
              color: 'var(--text-primary)',
              fontSize: '0.9rem',
              outline: 'none',
            }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.78rem', fontWeight: 800, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Filter size={14} /> TYPE:
          </span>
          <button
            onClick={() => setFilterType('')}
            style={{
              padding: '0.35rem 0.85rem',
              borderRadius: '9999px',
              fontSize: '0.78rem',
              fontWeight: 800,
              cursor: 'pointer',
              border: filterType === '' ? '1px solid var(--accent-primary)' : '1px solid var(--glass-border)',
              background: filterType === '' ? 'var(--status-active-bg)' : 'var(--bg-input)',
              color: filterType === '' ? 'var(--accent-primary)' : 'var(--text-secondary)',
            }}
          >
            All Vacant
          </button>
          <button
            onClick={() => setFilterType('CLASSROOM')}
            style={{
              padding: '0.35rem 0.85rem',
              borderRadius: '9999px',
              fontSize: '0.78rem',
              fontWeight: 800,
              cursor: 'pointer',
              border: filterType === 'CLASSROOM' ? '1px solid var(--accent-primary)' : '1px solid var(--glass-border)',
              background: filterType === 'CLASSROOM' ? 'var(--status-active-bg)' : 'var(--bg-input)',
              color: filterType === 'CLASSROOM' ? 'var(--accent-primary)' : 'var(--text-secondary)',
            }}
          >
            Classrooms
          </button>
          <button
            onClick={() => setFilterType('LABORATORY')}
            style={{
              padding: '0.35rem 0.85rem',
              borderRadius: '9999px',
              fontSize: '0.78rem',
              fontWeight: 800,
              cursor: 'pointer',
              border: filterType === 'LABORATORY' ? '1px solid var(--accent-primary)' : '1px solid var(--glass-border)',
              background: filterType === 'LABORATORY' ? 'var(--status-active-bg)' : 'var(--bg-input)',
              color: filterType === 'LABORATORY' ? 'var(--accent-primary)' : 'var(--text-secondary)',
            }}
          >
            Labs
          </button>
        </div>
      </div>

      {/* Grid of Free Rooms */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '0.75rem' }}>
        {filteredRooms.map((room) => {
          const roomNum = typeof room === 'string' ? room : (room.room_number || room.room);
          const roomType = typeof room === 'object' ? room.room_type : 'CLASSROOM';

          return (
            <button
              key={roomNum}
              onClick={() => onSelectRoom && onSelectRoom(roomNum)}
              className="glass-card"
              style={{
                padding: '0.95rem 0.75rem',
                textAlign: 'center',
                cursor: 'pointer',
                border: '1px solid rgba(16, 185, 129, 0.35)',
                background: 'var(--status-free-bg)',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ fontSize: '0.68rem', fontWeight: 800, color: 'var(--status-free)', textTransform: 'uppercase', marginBottom: '0.25rem', letterSpacing: '0.05em' }}>
                ✓ VACANT NOW
              </div>
              <div style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                {roomNum}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem', fontWeight: 600 }}>
                {roomType || 'Classroom'}
              </div>
            </button>
          );
        })}
      </div>

      {filteredRooms.length === 0 && !loading && (
        <div className="glass-card" style={{ textAlign: 'center', padding: '2.5rem 1rem' }}>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            No vacant rooms match your search criteria right now.
          </p>
        </div>
      )}
    </div>
  );
}
