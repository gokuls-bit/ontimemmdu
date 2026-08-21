import React from 'react';
import { Download, FileSpreadsheet, FileJson, CheckCircle2 } from 'lucide-react';
import { getDownloadUrl } from '../../api/timetableApi';

export function TimetableDownloads() {
  const semesters = [
    { sem: '3rd', title: '3rd Semester CSE', year: '2026-27' },
    { sem: '4th', title: '4th Semester CSE', year: '2026-27' },
    { sem: '5th', title: '5th Semester CSE', year: '2026-27' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div className="glass-card">
        <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', marginBottom: '0.35rem' }}>
          Official Timetable Downloads
        </h3>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          Download verified departmental Excel master timetables or structured JSON datasets.
        </p>
      </div>

      {semesters.map((item) => (
        <div key={item.sem} className="glass-card" style={{ borderLeft: '4px solid #6366f1' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
                {item.title}
              </h4>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Academic Session {item.year}
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#34d399', background: 'rgba(16, 185, 129, 0.12)', padding: '0.2rem 0.6rem', borderRadius: '6px' }}>
              VERIFIED
            </span>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <a
              href={getDownloadUrl(item.sem, 'excel')}
              download
              style={{
                flex: 1,
                minWidth: '140px',
                padding: '0.65rem 1rem',
                borderRadius: '10px',
                background: 'rgba(16, 185, 129, 0.15)',
                border: '1px solid rgba(16, 185, 129, 0.35)',
                color: '#34d399',
                fontWeight: 700,
                fontSize: '0.85rem',
                textDecoration: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                transition: 'all 0.2s ease',
              }}
            >
              <FileSpreadsheet size={18} /> Download Excel (.xlsx)
            </a>

            <a
              href={getDownloadUrl(item.sem, 'json')}
              download
              style={{
                flex: 1,
                minWidth: '140px',
                padding: '0.65rem 1rem',
                borderRadius: '10px',
                background: 'rgba(99, 102, 241, 0.15)',
                border: '1px solid rgba(99, 102, 241, 0.35)',
                color: '#a78bfa',
                fontWeight: 700,
                fontSize: '0.85rem',
                textDecoration: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                transition: 'all 0.2s ease',
              }}
            >
              <FileJson size={18} /> Download JSON
            </a>
          </div>
        </div>
      ))}
    </div>
  );
}
