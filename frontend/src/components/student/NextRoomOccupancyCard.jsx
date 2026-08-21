import React, { useState, useEffect } from 'react';
import { getRoomStatus } from '../../api/roomApi';
import { DoorOpen, CheckCircle, AlertCircle, Clock } from 'lucide-react';

export function NextRoomOccupancyCard({ nextRoom }) {
  const [roomData, setRoomData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!nextRoom) return;

    async function loadStatus() {
      setLoading(true);
      try {
        const data = await getRoomStatus(nextRoom);
        setRoomData(data);
      } catch (err) {
        console.error('Error fetching next room status:', err);
      } finally {
        setLoading(false);
      }
    }

    loadStatus();
  }, [nextRoom]);

  if (!nextRoom || !roomData) return null;

  const isFree = roomData.status === 'FREE';
  const activeClass = roomData.current_class;

  return (
    <div className="glass-card" style={{ borderTop: isFree ? '3px solid #10b981' : '3px solid #f59e0b' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
          <DoorOpen size={16} /> NEXT ROOM LIVE STATUS
        </div>

        <span
          style={{
            fontSize: '0.75rem',
            fontWeight: 800,
            padding: '0.2rem 0.6rem',
            borderRadius: '6px',
            background: isFree ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
            color: isFree ? '#34d399' : '#fbbf24',
            border: isFree ? '1px solid rgba(52, 211, 153, 0.3)' : '1px solid rgba(251, 191, 36, 0.3)',
          }}
        >
          {isFree ? '✓ FREE NOW' : '● OCCUPIED NOW'}
        </span>
      </div>

      <div style={{ fontSize: '0.95rem', color: 'var(--text-primary)', marginTop: '0.25rem' }}>
        {isFree ? (
          <p style={{ color: '#34d399', fontSize: '0.85rem' }}>
            Room {nextRoom} is currently vacant and ready for your next class.
          </p>
        ) : (
          <div>
            <div style={{ fontWeight: 700, color: '#fbbf24', fontSize: '0.9rem' }}>
              Currently occupied by {activeClass?.subject || 'another class'} ({activeClass?.section || ''})
            </div>
            {activeClass?.end_time && (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginTop: '0.2rem' }}>
                <Clock size={14} /> Ends at {activeClass.end_time}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
