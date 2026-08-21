import { apiClient } from './client';

export async function getAdminDashboard() {
  return apiClient('/admin/dashboard/');
}

export async function getAdminTimetable(filters = {}) {
  const params = new URLSearchParams(filters);
  return apiClient(`/admin/timetable/?${params.toString()}`);
}

export async function getAdminAlterations() {
  return apiClient('/admin/alterations/');
}

export async function createAlteration(data) {
  return apiClient('/admin/alterations/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function approveAlteration(overrideId) {
  return apiClient(`/admin/alterations/${overrideId}/approve/`, {
    method: 'POST',
  });
}

export async function emergencyRoomChange(data) {
  return apiClient('/admin/emergency-room-change/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function cancelClassInstance(data) {
  return apiClient('/admin/cancellations/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function createRoomMaintenance(data) {
  return apiClient('/admin/rooms/maintenance/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getAuditLogs() {
  return apiClient('/admin/audit/');
}
