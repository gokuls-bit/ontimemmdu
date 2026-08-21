import { apiClient } from './client';

export async function getMetadataSemesters() {
  return apiClient('/metadata/semesters/');
}

export async function getMetadataSections(semesterNumber) {
  const params = new URLSearchParams();
  if (semesterNumber) params.append('semester', semesterNumber);
  return apiClient(`/metadata/sections/?${params.toString()}`);
}

export async function getMetadataGroups(sectionId) {
  const params = new URLSearchParams();
  if (sectionId) params.append('section', sectionId);
  return apiClient(`/metadata/groups/?${params.toString()}`);
}
