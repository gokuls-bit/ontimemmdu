import React, { useState, useEffect } from 'react';
import { getAuditLogs } from '../api/adminApi';
import { ShieldCheck, Clock, User } from 'lucide-react';

export function AuditLogViewer() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadLogs() {
      setLoading(true);
      try {
        const data = await getAuditLogs();
        setLogs(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadLogs();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
          <ShieldCheck size={22} className="text-indigo-400" />
          <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc' }}>
            System Audit History Ledger
          </h3>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Immutable append-only ledger recording administrative changes.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {logs.map((log) => (
          <div key={log.id} className="glass-card" style={{ padding: '0.85rem 1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#c084fc', background: 'rgba(192, 132, 252, 0.12)', padding: '0.2rem 0.6rem', borderRadius: '6px' }}>
                {log.action}
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <Clock size={12} /> {new Date(log.created_at).toLocaleString()}
              </span>
            </div>

            <div style={{ fontSize: '0.9rem', color: '#fff', fontWeight: 600 }}>
              User: <span style={{ color: '#a78bfa' }}>{log.user_identifier}</span> | Target: {log.target_model} #{log.target_id}
            </div>

            {log.reason && (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                Reason: {log.reason}
              </div>
            )}
          </div>
        ))}

        {logs.length === 0 && !loading && (
          <div className="glass-card" style={{ textAlign: 'center', padding: '2rem' }}>
            <p style={{ color: 'var(--text-secondary)' }}>No audit log history entries recorded yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
