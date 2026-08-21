import { useState, useEffect } from 'react';
import { searchTeachers, getTeacherLocation, getTeacherSchedule } from '../api/teacherApi';

export function useTeacherLocator() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedTeacherLocation, setSelectedTeacherLocation] = useState(null);
  const [selectedTeacherSchedule, setSelectedTeacherSchedule] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Debounced Teacher Search (300ms)
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    const handler = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const results = await searchTeachers(searchQuery.trim());
        setSearchResults(results || []);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(handler);
  }, [searchQuery]);

  const inspectTeacher = async (teacherIdentifier) => {
    setLoading(true);
    setError(null);
    try {
      const loc = await getTeacherLocation(teacherIdentifier);
      const sched = await getTeacherSchedule(teacherIdentifier);
      setSelectedTeacherLocation(loc);
      setSelectedTeacherSchedule(sched);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  return {
    searchQuery,
    setSearchQuery,
    searchResults,
    selectedTeacherLocation,
    selectedTeacherSchedule,
    loading,
    error,
    inspectTeacher,
    clearSelectedTeacher: () => {
      setSelectedTeacherLocation(null);
      setSelectedTeacherSchedule(null);
    },
  };
}
