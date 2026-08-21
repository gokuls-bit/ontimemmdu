import React, { useState, useEffect } from 'react';
import { getAdminAlterations, approveAlteration } from '../api/adminApi';
import { CheckCircle, XCircle, AlertTriangle, ArrowRight } from 'lucide-react';

export function ApprovalCenter() {
  const [alterations, setAlterations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [actionSuccess, setActionSuccess] = useState(null);

  const loadAlterations = async () => {
    setLoading(true);
    try {
      const data = await getAdminAlterations();
      setAlterations(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlterations();
  }, []);

  const handleApprove = async (id) => {
    try {
      await approveAlteration(id);
      setActionSuccess(`Alteration #${id} approved successfully!`);
      loadAlterations();
    } catch (err) {
      alert(err.message || 'Error approving alteration');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div className="glass-card">
        <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc', marginBottom: '0.25rem' }}>
          Pending Approval Queue
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Review timetable alteration requests and execute conflict validation before activation.
        </p>
      </div>

      {actionSuccess && (
        <div style={{ padding: '0.75rem', borderRadius: '8px', background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)', color: '#34d399', fontSize: '0.85rem' }}>
          {actionSuccess}
        </div>
      )}

      {alterations.map((alt) => (
        <div key={alt.id} className="glass-card" style={{ borderLeft: '4px solid #f59e0b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <div>
              <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#fbbf24', textTransform: 'uppercase' }}>
                ALTERATION REQUEST #{alt.id}
              </span>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>
                {alt.subject_name} ({alt.date} Period {alt.period})
              </h4>
            </div>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#a78bfa', background: 'rgba(139,92,246,0.15)', padding: '0.2rem 0.6rem', borderRadius: '6px' }}>
              PENDING APPROVAL
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(0,0,0,0.25)', padding: '0.85rem', borderRadius: '10px', marginBottom: '1rem', fontSize: '0.85rem' }}>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>DESTINATION ROOM</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#c084fc' }}>ROOM {alt.room_number}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>FACULTY</div>
              <div style={{ fontWeight: 700, color: '#fff' }}>{alt.teacher_name}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>REASON</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{alt.reason || 'N/A'}</div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              onClick={() => handleApprove(alt.id)}
              style={{
                flex: 1,
                padding: '0.6rem',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                border: 'none',
                color: '#fff',
                fontWeight: 700,
                fontSize: '0.85rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.4rem',
              }}
            >
              <CheckCircle size={16} /> Re-validate & Approve
            </button>
          </div>
        </div>
      ))}

      {alterations.length === 0 && !loading && (
        <div className="glass-card" style={{ textAlign: 'center', padding: '2rem' }}>
          <p style={{ color: 'var(--text-secondary)' }}>No pending timetable alterations in queue.</p>
        </div>
      )}
    </div>
  );
}
