import React, { useState, useEffect } from 'react';
import { getAdminDashboard } from '../api/adminApi';
import { ApprovalCenter } from './ApprovalCenter';
import { EmergencyRoomChangeModal } from './EmergencyRoomChangeModal';
import { RoomMaintenanceManager } from './RoomMaintenanceManager';
import { AuditLogViewer } from './AuditLogViewer';
import { Shield, Zap, Users, DoorOpen, Wrench, FileSpreadsheet, CheckCircle } from 'lucide-react';

export function AdminDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [activeSubTab, setActiveSubTab] = useState('approvals');
  const [isEmergencyModalOpen, setIsEmergencyModalOpen] = useState(false);

  const loadMetrics = async () => {
    try {
      const data = await getAdminDashboard();
      setMetrics(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadMetrics();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Header & Quick Emergency Action Button */}
      <div className="glass-card" style={{ borderLeft: '4px solid #6366f1' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
              <Shield className="text-indigo-400" size={16} /> CSE SMARTROOM CONTROL CENTER
            </div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f8fafc' }}>
              Administrative Operations
            </h2>
          </div>

          <button
            onClick={() => setIsEmergencyModalOpen(true)}
            style={{
              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
              border: 'none',
              color: '#fff',
              padding: '0.55rem 1rem',
              borderRadius: '10px',
              fontWeight: 800,
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              cursor: 'pointer',
              boxShadow: '0 4px 14px rgba(245, 158, 11, 0.35)',
            }}
          >
            <Zap size={18} /> EMERGENCY ROOM CHANGE
          </button>
        </div>
      </div>

      {/* Metrics Overview Grid */}
      {metrics && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.75rem' }}>
          <div className="glass-card" style={{ padding: '0.85rem', textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>STUDENTS</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff' }}>{metrics.total_students}</div>
          </div>
          <div className="glass-card" style={{ padding: '0.85rem', textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>TEACHERS</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff' }}>{metrics.total_teachers}</div>
          </div>
          <div className="glass-card" style={{ padding: '0.85rem', textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>TOTAL ROOMS</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff' }}>{metrics.total_rooms}</div>
          </div>
          <div className="glass-card" style={{ padding: '0.85rem', textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 800, color: '#c084fc', textTransform: 'uppercase' }}>ACTIVE CLASSES</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#c084fc' }}>{metrics.active_classes}</div>
          </div>
          <div className="glass-card" style={{ padding: '0.85rem', textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 800, color: '#34d399', textTransform: 'uppercase' }}>FREE ROOMS</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#34d399' }}>{metrics.free_rooms}</div>
          </div>
        </div>
      )}

      {/* Navigation Sub-Tabs */}
      <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
        <button
          onClick={() => setActiveSubTab('approvals')}
          style={{
            padding: '0.5rem 0.85rem',
            borderRadius: '8px',
            fontSize: '0.8rem',
            fontWeight: 700,
            cursor: 'pointer',
            border: activeSubTab === 'approvals' ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.08)',
            background: activeSubTab === 'approvals' ? 'rgba(99,102,241,0.2)' : 'rgba(255,255,255,0.04)',
            color: activeSubTab === 'approvals' ? '#a78bfa' : 'var(--text-secondary)',
          }}
        >
          Approval Queue
        </button>

        <button
          onClick={() => setActiveSubTab('maintenance')}
          style={{
            padding: '0.5rem 0.85rem',
            borderRadius: '8px',
            fontSize: '0.8rem',
            fontWeight: 700,
            cursor: 'pointer',
            border: activeSubTab === 'maintenance' ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.08)',
            background: activeSubTab === 'maintenance' ? 'rgba(99,102,241,0.2)' : 'rgba(255,255,255,0.04)',
            color: activeSubTab === 'maintenance' ? '#a78bfa' : 'var(--text-secondary)',
          }}
        >
          Maintenance & Cancellations
        </button>

        <button
          onClick={() => setActiveSubTab('audit')}
          style={{
            padding: '0.5rem 0.85rem',
            borderRadius: '8px',
            fontSize: '0.8rem',
            fontWeight: 700,
            cursor: 'pointer',
            border: activeSubTab === 'audit' ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.08)',
            background: activeSubTab === 'audit' ? 'rgba(99,102,241,0.2)' : 'rgba(255,255,255,0.04)',
            color: activeSubTab === 'audit' ? '#a78bfa' : 'var(--text-secondary)',
          }}
        >
          Audit History
        </button>
      </div>

      {activeSubTab === 'approvals' && <ApprovalCenter />}
      {activeSubTab === 'maintenance' && <RoomMaintenanceManager />}
      {activeSubTab === 'audit' && <AuditLogViewer />}

      <EmergencyRoomChangeModal
        isOpen={isEmergencyModalOpen}
        onClose={() => setIsEmergencyModalOpen(false)}
        onSuccess={() => {
          loadMetrics();
          setActiveSubTab('approvals');
        }}
      />
    </div>
  );
}
