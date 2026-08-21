import { apiClient } from './client';

export async function getRoomStatus(roomNumber) {
  return apiClient(`/rooms/${encodeURIComponent(roomNumber)}/status/`);
}

export async function getFreeRooms(roomType) {
  const params = new URLSearchParams();
  if (roomType) params.append('room_type', roomType);
  return apiClient(`/rooms/free/?${params.toString()}`);
}

export async function getOccupiedRooms(roomType) {
  const params = new URLSearchParams();
  if (roomType) params.append('room_type', roomType);
  return apiClient(`/rooms/occupied/?${params.toString()}`);
}

export async function getAllRoomStatuses(status, roomType) {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (roomType) params.append('room_type', roomType);
  return apiClient(`/rooms/status/?${params.toString()}`);
}

export async function getRoomSchedule(roomNumber, day) {
  const params = new URLSearchParams();
  if (day) params.append('day', day);
  return apiClient(`/rooms/${encodeURIComponent(roomNumber)}/schedule/?${params.toString()}`);
}

export async function getRoomNextFree(roomNumber) {
  return apiClient(`/rooms/${encodeURIComponent(roomNumber)}/next-free/`);
}

export async function searchRooms(query) {
  const params = new URLSearchParams({ q: query });
  return apiClient(`/rooms/search/?${params.toString()}`);
}

export async function findAvailableRooms(startTime, endTime, roomType) {
  const params = new URLSearchParams({ start_time: startTime, end_time: endTime });
  if (roomType) params.append('room_type', roomType);
  return apiClient(`/rooms/find-available/?${params.toString()}`);
}
