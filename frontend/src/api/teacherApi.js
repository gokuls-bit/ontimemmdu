import { apiClient } from './client';

export async function searchTeachers(query) {
  const params = new URLSearchParams({ q: query });
  return apiClient(`/teachers/search/?${params.toString()}`);
}

export async function getTeacherLocation(teacherIdOrName) {
  return apiClient(`/teachers/${encodeURIComponent(teacherIdOrName)}/location/`);
}

export async function getTeacherNextClass(teacherIdOrName) {
  return apiClient(`/teachers/${encodeURIComponent(teacherIdOrName)}/next-class/`);
}

export async function getTeacherSchedule(teacherIdOrName, day) {
  const params = new URLSearchParams();
  if (day) params.append('day', day);
  return apiClient(`/teachers/${encodeURIComponent(teacherIdOrName)}/schedule/?${params.toString()}`);
}

export async function getAllTeacherStatuses() {
  return apiClient('/teachers/status/');
}
