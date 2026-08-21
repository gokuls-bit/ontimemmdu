import React from 'react';
import { ArrowRight, CheckCircle2, Navigation } from 'lucide-react';

export function RoomTransitionCard({ currentRoom, nextRoom, leaveTime }) {
  if (!currentRoom || !nextRoom) return null;

  const isSameRoom = String(currentRoom).trim().toUpperCase() === String(nextRoom).trim().toUpperCase();

  return (
    <div className="glass-card" style={{ background: isSameRoom ? 'rgba(16, 185, 129, 0.08)' : 'rgba(99, 102, 241, 0.08)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
        <Navigation size={18} className={isSameRoom ? 'text-emerald-400' : 'text-indigo-400'} />
        <h4 style={{ fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: isSameRoom ? '#34d399' : '#a78bfa', letterSpacing: '0.05em' }}>
          ROOM TRANSITION GUIDANCE
        </h4>
      </div>

      {isSameRoom ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <CheckCircle2 size={24} className="text-emerald-400" />
          <div>
            <div style={{ fontWeight: 800, fontSize: '1.1rem', color: '#f8fafc' }}>
              ROOM {currentRoom}
            </div>
            <div style={{ fontSize: '0.85rem', color: '#34d399' }}>
              Remain in the same room for your next class.
            </div>
          </div>
        </div>
      ) : (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(0, 0, 0, 0.25)', padding: '0.85rem 1.25rem', borderRadius: '12px', marginBottom: '0.5rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>CURRENT ROOM</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc' }}>{currentRoom}</div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.2rem' }}>
              <ArrowRight size={22} className="text-indigo-400 animate-pulse" />
              {leaveTime && (
                <span style={{ fontSize: '0.7rem', color: '#a78bfa', fontWeight: 600 }}>
                  Leave after {leaveTime}
                </span>
              )}
            </div>

            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>NEXT ROOM</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#c084fc' }}>{nextRoom}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
