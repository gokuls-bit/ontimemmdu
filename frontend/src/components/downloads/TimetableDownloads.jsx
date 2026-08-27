import React from 'react';
import { Download, FileSpreadsheet, FileJson, CheckCircle2, FileText } from 'lucide-react';
import { getDownloadUrl } from '../../api/timetableApi';

export function TimetableDownloads() {
  const semesters = [
    { sem: '3rd', title: '3rd Semester CSE Master Schedule', year: 'Academic Year 2026-27' },
    { sem: '4th', title: '4th Semester CSE Master Schedule', year: 'Academic Year 2026-27' },
    { sem: '5th', title: '5th Semester CSE Master Schedule', year: 'Academic Year 2026-27' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.35rem' }}>
          <FileText style={{ color: 'var(--accent-primary)' }} size={22} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            Official Timetable Downloads
          </h3>
        </div>
        <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
          Download verified departmental Excel master schedules or structured JSON files.
        </p>
      </div>

      {semesters.map((item) => (
        <div key={item.sem} className="glass-card" style={{ borderLeft: '4px solid var(--accent-primary)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                {item.title}
              </h4>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {item.year}
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--status-free)', background: 'var(--status-free-bg)', padding: '0.25rem 0.65rem', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
              ✓ VERIFIED
            </span>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <a
              href={getDownloadUrl(item.sem, 'excel')}
              download
              style={{
                flex: 1,
                minWidth: '150px',
                padding: '0.7rem 1rem',
                borderRadius: '12px',
                background: 'var(--status-free-bg)',
                border: '1px solid rgba(16, 185, 129, 0.35)',
                color: 'var(--status-free)',
                fontWeight: 800,
                fontSize: '0.88rem',
                textDecoration: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                transition: 'all 0.2s ease',
              }}
            >
              <FileSpreadsheet size={18} /> Excel Sheet (.xlsx)
            </a>

            <a
              href={getDownloadUrl(item.sem, 'json')}
              download
              style={{
                flex: 1,
                minWidth: '150px',
                padding: '0.7rem 1rem',
                borderRadius: '12px',
                background: 'var(--status-active-bg)',
                border: '1px solid rgba(139, 92, 246, 0.35)',
                color: 'var(--status-active)',
                fontWeight: 800,
                fontSize: '0.88rem',
                textDecoration: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                transition: 'all 0.2s ease',
              }}
            >
              <FileJson size={18} /> JSON Dataset
            </a>
          </div>
        </div>
      ))}
    </div>
  );
}
