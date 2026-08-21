import React, { useState } from 'react';
import { createRoomMaintenance, cancelClassInstance } from '../api/adminApi';
import { Wrench, XCircle, CheckCircle, AlertTriangle } from 'lucide-react';

export function RoomMaintenanceManager() {
  const [maintRoom, setMaintRoom] = useState('');
  const [maintDate, setMaintDate] = useState(new Date().toISOString().split('T')[0]);
  const [maintReason, setMaintReason] = useState('Electrical Repair & Projector Maintenance');
  const [maintSuccess, setMaintSuccess] = useState(null);

  const [cancelEntryId, setCancelEntryId] = useState('');
  const [cancelDate, setCancelDate] = useState(new Date().toISOString().split('T')[0]);
  const [cancelReason, setCancelReason] = useState('Faculty on official duty');
  const [cancelSuccess, setCancelSuccess] = useState(null);

  const handleMaintenance = async (e) => {
    e.preventDefault();
    try {
      await createRoomMaintenance({
        room: maintRoom,
        date: maintDate,
        reason: maintReason,
      });
      setMaintSuccess(`Room ${maintRoom} closed for maintenance on ${maintDate}.`);
      setMaintRoom('');
    } catch (err) {
      alert(err.message || 'Failed to create room maintenance');
    }
  };

  const handleCancellation = async (e) => {
    e.preventDefault();
    try {
      await cancelClassInstance({
        timetable_entry_id: Number(cancelEntryId),
        date: cancelDate,
        reason: cancelReason,
      });
      setCancelSuccess(`Class entry #${cancelEntryId} cancelled for ${cancelDate}.`);
      setCancelEntryId('');
    } catch (err) {
      alert(err.message || 'Failed to cancel class instance');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* 1. Room Maintenance Closure Form */}
      <div className="glass-card" style={{ borderLeft: '4px solid #ef4444' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
          <Wrench size={20} className="text-red-400" />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff' }}>Room Maintenance Closure</h3>
        </div>

        {maintSuccess && (
          <div style={{ color: '#34d399', fontSize: '0.85rem', marginBottom: '0.75rem' }}>{maintSuccess}</div>
        )}

        <form onSubmit={handleMaintenance} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <input type="text" value={maintRoom} onChange={(e) => setMaintRoom(e.target.value)} required placeholder="Room Number (e.g. 357)" style={{ flex: 1, padding: '0.6rem', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.12)', color: '#fff' }} />
            <input type="date" value={maintDate} onChange={(e) => setMaintDate(e.target.value)} required style={{ flex: 1, padding: '0.6rem', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.12)', color: '#fff' }} />
          </div>
          <input type="text" value={maintReason} onChange={(e) => setMaintReason(e.target.value)} required placeholder="Reason for closure" style={{ padding: '0.6rem', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.12)', color: '#fff' }} />
          <button type="submit" style={{ padding: '0.6rem', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.2)', border: '1px solid rgba(239, 68, 68, 0.4)', color: '#f87171', fontWeight: 700, cursor: 'pointer' }}>
            Close Room for Maintenance
          </button>
        </form>
      </div>

      {/* 2. Single Instance Class Cancellation Form */}
      <div className="glass-card" style={{ borderLeft: '4px solid #f59e0b' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
          <XCircle size={20} className="text-amber-400" />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff' }}>Cancel Class Instance</h3>
        </div>

        {cancelSuccess && (
          <div style={{ color: '#34d399', fontSize: '0.85rem', marginBottom: '0.75rem' }}>{cancelSuccess}</div>
        )}

        <form onSubmit={handleCancellation} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <input type="number" value={cancelEntryId} onChange={(e) => setCancelEntryId(e.target.value)} required placeholder="Timetable Entry ID (e.g. 1)" style={{ flex: 1, padding: '0.6rem', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.12)', color: '#fff' }} />
            <input type="date" value={cancelDate} onChange={(e) => setCancelDate(e.target.value)} required style={{ flex: 1, padding: '0.6rem', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.12)', color: '#fff' }} />
          </div>
          <input type="text" value={cancelReason} onChange={(e) => setCancelReason(e.target.value)} required placeholder="Reason for cancellation" style={{ padding: '0.6rem', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.12)', color: '#fff' }} />
          <button type="submit" style={{ padding: '0.6rem', borderRadius: '8px', background: 'rgba(245, 158, 11, 0.2)', border: '1px solid rgba(245, 158, 11, 0.4)', color: '#fbbf24', fontWeight: 700, cursor: 'pointer' }}>
            Cancel Class Instance
          </button>
        </form>
      </div>
    </div>
  );
}
