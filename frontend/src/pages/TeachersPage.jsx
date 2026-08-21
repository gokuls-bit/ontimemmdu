import React from 'react';
import { TeacherLocator } from '../components/teachers/TeacherLocator';
import { useTeacherLocator } from '../hooks/useTeacherLocator';
import { Users } from 'lucide-react';

export function TeachersPage() {
  const teacherLocator = useTeacherLocator();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
          <Users className="text-indigo-400" size={22} />
          <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc' }}>
            Faculty Location Intelligence
          </h3>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Locate CSE department faculty members and view live room assignments.
        </p>
      </div>

      <TeacherLocator {...teacherLocator} />
    </div>
  );
}
