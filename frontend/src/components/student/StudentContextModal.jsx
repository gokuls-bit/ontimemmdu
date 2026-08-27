import React, { useState, useEffect } from 'react';
import { getMetadataSemesters, getMetadataSections } from '../../api/metadataApi';
import { GraduationCap, CheckCircle, AlertCircle, Sparkles, X } from 'lucide-react';

export function StudentContextModal({ isOpen, onClose, onSave, currentContext }) {
  const [semesters, setSemesters] = useState([]);
  const [sections, setSections] = useState([]);
  const [groups, setGroups] = useState([]);

  const [selectedSemester, setSelectedSemester] = useState(currentContext?.semester || '');
  const [selectedSection, setSelectedSection] = useState(currentContext?.section || '');
  const [selectedGroup, setSelectedGroup] = useState(currentContext?.group || '');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch active semesters on mount
  useEffect(() => {
    async function loadSemesters() {
      setLoading(true);
      try {
        const data = await getMetadataSemesters();
        setSemesters(data || []);
      } catch (err) {
        setError('Could not load semester list.');
      } finally {
        setLoading(false);
      }
    }
    loadSemesters();
  }, []);

  // Fetch sections when semester changes
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

  // Fetch groups when section changes
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
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(10px)',
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
          maxWidth: '460px',
          background: 'var(--bg-card-solid)',
          border: '1px solid var(--glass-border)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
          padding: '1.75rem',
          position: 'relative',
        }}
      >
        {onClose && currentContext && (
          <button
            onClick={onClose}
            style={{
              position: 'absolute',
              top: '1rem',
              right: '1rem',
              background: 'var(--bg-input)',
              border: 'none',
              borderRadius: '50%',
              width: '32px',
              height: '32px',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <X size={18} />
          </button>
        )}

        {/* Modal Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '1.5rem' }}>
          <div
            style={{
              width: '46px',
              height: '46px',
              borderRadius: '14px',
              background: 'var(--accent-primary-gradient)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              boxShadow: '0 6px 16px var(--accent-glow)',
            }}
          >
            <GraduationCap size={26} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-primary)' }}>
              Welcome to MMDU Central! 👋
            </h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
              Select your semester and section to get personalized room & schedule info.
            </p>
          </div>
        </div>

        {error && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--status-cancelled)', fontSize: '0.85rem', marginBottom: '1rem', background: 'var(--status-cancelled-bg)', padding: '0.6rem 0.85rem', borderRadius: '10px' }}>
            <AlertCircle size={16} /> {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
          {/* Semester Selector */}
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
              Academic Semester
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
                padding: '0.8rem 1rem',
                borderRadius: '12px',
                background: 'var(--bg-input)',
                border: '1px solid var(--glass-border)',
                color: 'var(--text-primary)',
                fontSize: '0.95rem',
                fontWeight: 600,
                outline: 'none',
              }}
            >
              <option value="" disabled style={{ background: 'var(--bg-card-solid)' }}>-- Select Semester --</option>
              {semesters.map((sem) => (
                <option key={sem.id} value={sem.number} style={{ background: 'var(--bg-card-solid)' }}>
                  {sem.number}th Semester ({sem.academic_year})
                </option>
              ))}
              {semesters.length === 0 && (
                <>
                  <option value="3" style={{ background: 'var(--bg-card-solid)' }}>3rd Semester (CSE)</option>
                  <option value="5" style={{ background: 'var(--bg-card-solid)' }}>5th Semester (CSE)</option>
                </>
              )}
            </select>
          </div>

          {/* Section Selector */}
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
              Section / Class
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
                padding: '0.8rem 1rem',
                borderRadius: '12px',
                background: 'var(--bg-input)',
                border: '1px solid var(--glass-border)',
                color: 'var(--text-primary)',
                fontSize: '0.95rem',
                fontWeight: 600,
                outline: 'none',
                opacity: selectedSemester ? 1 : 0.5,
              }}
            >
              <option value="" disabled style={{ background: 'var(--bg-card-solid)' }}>-- Select Section --</option>
              {sections.map((sec) => (
                <option key={sec.id} value={sec.name} style={{ background: 'var(--bg-card-solid)' }}>
                  {sec.name}
                </option>
              ))}
              {sections.length === 0 && selectedSemester && (
                <>
                  <option value="5CSEA1" style={{ background: 'var(--bg-card-solid)' }}>5CSEA1</option>
                  <option value="5CSEA2" style={{ background: 'var(--bg-card-solid)' }}>5CSEA2</option>
                  <option value="3CSEA1" style={{ background: 'var(--bg-card-solid)' }}>3CSEA1</option>
                </>
              )}
            </select>
          </div>

          {/* Group Selector */}
          {groups.length > 0 && (
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                Lab Subgroup (Optional)
              </label>
              <select
                value={selectedGroup}
                onChange={(e) => setSelectedGroup(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.8rem 1rem',
                  borderRadius: '12px',
                  background: 'var(--bg-input)',
                  border: '1px solid var(--glass-border)',
                  color: 'var(--text-primary)',
                  fontSize: '0.95rem',
                  fontWeight: 600,
                  outline: 'none',
                }}
              >
                <option value="" style={{ background: 'var(--bg-card-solid)' }}>Entire Section / No Group</option>
                {groups.map((grp) => (
                  <option key={grp.id} value={grp.name} style={{ background: 'var(--bg-card-solid)' }}>
                    Group {grp.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.75rem' }}>
            {onClose && currentContext && (
              <button
                type="button"
                onClick={onClose}
                style={{
                  flex: 1,
                  padding: '0.8rem',
                  borderRadius: '12px',
                  background: 'var(--bg-input)',
                  border: '1px solid var(--glass-border)',
                  color: 'var(--text-secondary)',
                  fontWeight: 700,
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
                padding: '0.8rem',
                borderRadius: '12px',
                background: 'var(--accent-primary-gradient)',
                border: 'none',
                color: '#fff',
                fontWeight: 800,
                fontSize: '0.95rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                boxShadow: '0 6px 18px var(--accent-glow)',
              }}
            >
              <CheckCircle size={18} /> Save Preferences
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
