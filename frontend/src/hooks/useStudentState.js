import { useState, useEffect, useCallback, useRef } from 'react';
import { getStudentState } from '../api/studentApi';

const STORAGE_KEY = 'cse_smartroom_student_context';

export function useStudentState() {
  const [context, setContext] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const prevPeriodRef = useRef(null);

  const fetchState = useCallback(async (isSilent = false) => {
    if (!context || !context.semester || !context.section) return;

    if (!isSilent) setLoading(true);
    setError(null);

    try {
      const data = await getStudentState(context.semester, context.section, context.group);
      setState(data);
      setLastUpdated(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));

      const currentPeriodNum = data?.current_period?.period;
      if (prevPeriodRef.current !== null && prevPeriodRef.current !== currentPeriodNum) {
        console.log(`Period boundary crossed: ${prevPeriodRef.current} -> ${currentPeriodNum}. Refreshing state.`);
      }
      prevPeriodRef.current = currentPeriodNum;
    } catch (err) {
      console.error('Error fetching student state:', err);
      setError(err);
    } finally {
      if (!isSilent) setLoading(false);
    }
  }, [context]);

  // Initial fetch and 30-second polling
  useEffect(() => {
    if (!context) return;

    fetchState(false);
    const interval = setInterval(() => {
      fetchState(true);
    }, 30000);

    return () => clearInterval(interval);
  }, [context, fetchState]);

  const saveContext = (newContext) => {
    setContext(newContext);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newContext));
    } catch (e) {
      console.error('Failed to save context to localStorage:', e);
    }
  };

  const clearContext = () => {
    setContext(null);
    setState(null);
    localStorage.removeItem(STORAGE_KEY);
  };

  return {
    context,
    state,
    loading,
    error,
    lastUpdated,
    refreshState: () => fetchState(false),
    saveContext,
    clearContext,
  };
}
