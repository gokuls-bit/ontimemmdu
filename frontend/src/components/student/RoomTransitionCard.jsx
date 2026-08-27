import React from 'react';
import { ArrowRight, CheckCircle2, Navigation, Footprints } from 'lucide-react';

export function RoomTransitionCard({ currentRoom, nextRoom, leaveTime }) {
  if (!currentRoom || !nextRoom) return null;

  const isSameRoom = String(currentRoom).trim().toUpperCase() === String(nextRoom).trim().toUpperCase();

  return (
    <div
      className="glass-card"
      style={{
        background: isSameRoom ? 'var(--status-free-bg)' : 'var(--status-active-bg)',
        border: isSameRoom ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(139, 92, 246, 0.3)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.75rem' }}>
        <Footprints size={18} style={{ color: isSameRoom ? 'var(--status-free)' : 'var(--status-active)' }} />
        <h4 style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: isSameRoom ? 'var(--status-free)' : 'var(--status-active)', letterSpacing: '0.06em' }}>
          WHERE TO HEAD NEXT 🚶
        </h4>
      </div>

      {isSameRoom ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: 'var(--status-free-bg)', color: 'var(--status-free)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <CheckCircle2 size={24} />
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: '1.15rem', color: 'var(--text-primary)' }}>
              Stay Put in Room {currentRoom}!
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--status-free)', fontWeight: 600 }}>
              Your next class is in the exact same classroom. No walking needed.
            </div>
          </div>
        </div>
      ) : (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--bg-input)', padding: '0.85rem 1.25rem', borderRadius: '14px', border: '1px solid var(--glass-border)' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>CURRENT</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>RM {currentRoom}</div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.2rem' }}>
              <ArrowRight size={22} style={{ color: 'var(--accent-primary)' }} className="animate-pulse" />
              {leaveTime && (
                <span style={{ fontSize: '0.7rem', color: 'var(--accent-primary)', fontWeight: 700 }}>
                  Head out at {leaveTime}
                </span>
              )}
            </div>

            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>NEXT LOCATION</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--status-active)' }}>RM {nextRoom}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
