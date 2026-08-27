import { apiClient } from './client';

export async function getStudentState(semester, section, group) {
  const params = new URLSearchParams({ semester, section });
  if (group) params.append('group', group);
  return apiClient(`/student/state/?${params.toString()}`);
}

export async function getCurrentClass(semester, section, group) {
  const params = new URLSearchParams({ semester, section });
  if (group) params.append('group', group);
  return apiClient(`/student/current-class/?${params.toString()}`);
}

export async function getNextClass(semester, section, group) {
  const params = new URLSearchParams({ semester, section });
  if (group) params.append('group', group);
  return apiClient(`/student/next-class/?${params.toString()}`);
}

export async function getStudentSchedule(semester, section, group, day, order = 'asc') {
  const params = new URLSearchParams({ semester, section });
  if (group) params.append('group', group);
  if (day) params.append('day', day);
  if (order) params.append('order', order);
  return apiClient(`/student/schedule/?${params.toString()}`);
}
