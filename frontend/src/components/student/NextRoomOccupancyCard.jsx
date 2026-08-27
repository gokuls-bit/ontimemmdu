import React, { useState, useEffect } from 'react';
import { getRoomStatus } from '../../api/roomApi';
import { DoorOpen, CheckCircle, AlertTriangle, Clock } from 'lucide-react';

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
    <div className="glass-card" style={{ borderTop: isFree ? '3px solid var(--status-free)' : '3px solid var(--status-occupied)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
          <DoorOpen size={16} /> ROOM {nextRoom} LIVE CHECK
        </div>

        <span
          style={{
            fontSize: '0.75rem',
            fontWeight: 800,
            padding: '0.2rem 0.6rem',
            borderRadius: '6px',
            background: isFree ? 'var(--status-free-bg)' : 'var(--status-occupied-bg)',
            color: isFree ? 'var(--status-free)' : 'var(--status-occupied)',
            border: isFree ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(245, 158, 11, 0.3)',
          }}
        >
          {isFree ? '✓ VACANT RIGHT NOW' : '● OCCUPIED AT THE MOMENT'}
        </span>
      </div>

      <div style={{ fontSize: '0.92rem', color: 'var(--text-primary)', marginTop: '0.25rem' }}>
        {isFree ? (
          <p style={{ color: 'var(--status-free)', fontSize: '0.88rem', fontWeight: 600 }}>
            Room {nextRoom} is completely empty right now. Feel free to walk over early!
          </p>
        ) : (
          <div>
            <div style={{ fontWeight: 700, color: 'var(--status-occupied)', fontSize: '0.9rem' }}>
              Another class is currently inside: {activeClass?.subject || 'Lecture in progress'} ({activeClass?.section || ''})
            </div>
            {activeClass?.end_time && (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.35rem', marginTop: '0.25rem' }}>
                <Clock size={14} style={{ color: 'var(--status-occupied)' }} /> Room frees up at {activeClass.end_time}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
