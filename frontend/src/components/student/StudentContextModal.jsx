import React, { useState, useEffect } from 'react';
import { getMetadataSemesters, getMetadataSections, getMetadataGroups } from '../../api/metadataApi';
import { GraduationCap, CheckCircle, AlertCircle } from 'lucide-react';

export function StudentContextModal({ isOpen, onClose, onSave, currentContext }) {
  const [semesters, setSemesters] = useState([]);
  const [sections, setSections] = useState([]);
  const [groups, setGroups] = useState([]);

  const [selectedSemester, setSelectedSemester] = useState(currentContext?.semester || '');
  const [selectedSection, setSelectedSection] = useState(currentContext?.section || '');
  const [selectedGroup, setSelectedGroup] = useState(currentContext?.group || '');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 1. Fetch active semesters on mount
  useEffect(() => {
    async function loadSemesters() {
      setLoading(true);
      try {
        const data = await getMetadataSemesters();
        setSemesters(data || []);
      } catch (err) {
        setError('Failed to load academic semesters.');
      } finally {
        setLoading(false);
      }
    }
    loadSemesters();
  }, []);

  // 2. Fetch sections when semester changes
  useEffect(() => {
    if (!selectedSemester) {
      setSections([]);
      setGroups([]);
      return;
    }
    async function loadSections() {
      try {
        const data = await getMetadataSections(selectedSemester);
        setSections(data || []);
      } catch (err) {
        console.error(err);
      }
    }
    loadSections();
  }, [selectedSemester]);

  // 3. Fetch groups when section changes
  useEffect(() => {
    if (!selectedSection) {
      setGroups([]);
      return;
    }
    const matchingSection = sections.find((s) => s.name === selectedSection || String(s.id) === String(selectedSection));
    if (matchingSection && matchingSection.groups) {
      setGroups(matchingSection.groups);
    } else {
      setGroups([]);
    }
  }, [selectedSection, sections]);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedSemester || !selectedSection) return;

    onSave({
      semester: selectedSemester,
      section: selectedSection,
      group: selectedGroup || null,
    });
    if (onClose) onClose();
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(8px)',
        zIndex: 2000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem',
      }}
    >
      <div
        className="glass-card"
        style={{
          width: '100%',
          maxWidth: '440px',
          background: 'rgba(19, 27, 46, 0.95)',
          border: '1px solid rgba(139, 92, 246, 0.3)',
          boxShadow: '0 20px 50px rgba(0, 0, 0, 0.5)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
          <div
            style={{
              width: '42px',
              height: '42px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
            }}
          >
            <GraduationCap size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc' }}>
              Select Academic Context
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Configure your semester & section to get live timetable intelligence.
            </p>
          </div>
        </div>

        {error && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f87171', fontSize: '0.85rem', marginBottom: '1rem' }}>
            <AlertCircle size={16} /> {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Semester Selector */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Semester
            </label>
            <select
              value={selectedSemester}
              onChange={(e) => {
                setSelectedSemester(e.target.value);
                setSelectedSection('');
                setSelectedGroup('');
              }}
              required
              style={{
                width: '100%',
                padding: '0.75rem',
                borderRadius: '10px',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                color: '#fff',
                fontSize: '0.95rem',
                outline: 'none',
              }}
            >
              <option value="" disabled style={{ background: '#131b2e' }}>-- Select Semester --</option>
              {semesters.map((sem) => (
                <option key={sem.id} value={sem.number} style={{ background: '#131b2e' }}>
                  {sem.number}th Semester ({sem.academic_year})
                </option>
              ))}
              {semesters.length === 0 && (
                <>
                  <option value="3" style={{ background: '#131b2e' }}>3rd Semester</option>
                  <option value="4" style={{ background: '#131b2e' }}>4th Semester</option>
                  <option value="5" style={{ background: '#131b2e' }}>5th Semester</option>
                </>
              )}
            </select>
          </div>

          {/* Section Selector */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Section
            </label>
            <select
              value={selectedSection}
              onChange={(e) => {
                setSelectedSection(e.target.value);
                setSelectedGroup('');
              }}
              required
              disabled={!selectedSemester}
              style={{
                width: '100%',
                padding: '0.75rem',
                borderRadius: '10px',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                color: '#fff',
                fontSize: '0.95rem',
                outline: 'none',
                opacity: selectedSemester ? 1 : 0.5,
              }}
            >
              <option value="" disabled style={{ background: '#131b2e' }}>-- Select Section --</option>
              {sections.map((sec) => (
                <option key={sec.id} value={sec.name} style={{ background: '#131b2e' }}>
                  {sec.name}
                </option>
              ))}
              {sections.length === 0 && selectedSemester && (
                <>
                  <option value={`5CSEA1`} style={{ background: '#131b2e' }}>5CSEA1</option>
                  <option value={`5CSEA2`} style={{ background: '#131b2e' }}>5CSEA2</option>
                </>
              )}
            </select>
          </div>

          {/* Group Selector (Conditional if section has groups) */}
          {groups.length > 0 && (
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                Group (Lab Subgroup)
              </label>
              <select
                value={selectedGroup}
                onChange={(e) => setSelectedGroup(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '10px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  color: '#fff',
                  fontSize: '0.95rem',
                  outline: 'none',
                }}
              >
                <option value="" style={{ background: '#131b2e' }}>Entire Section / No Group</option>
                {groups.map((grp) => (
                  <option key={grp.id} value={grp.name} style={{ background: '#131b2e' }}>
                    Group {grp.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
            {onClose && currentContext && (
              <button
                type="button"
                onClick={onClose}
                style={{
                  flex: 1,
                  padding: '0.75rem',
                  borderRadius: '10px',
                  background: 'rgba(255, 255, 255, 0.08)',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  color: 'var(--text-secondary)',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Cancel
              </button>
            )}
            <button
              type="submit"
              style={{
                flex: 2,
                padding: '0.75rem',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                border: 'none',
                color: '#fff',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                boxShadow: '0 4px 14px rgba(99, 102, 241, 0.4)',
              }}
            >
              <CheckCircle size={18} /> Save & Enter SmartRoom
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
