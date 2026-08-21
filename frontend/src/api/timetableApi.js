export function getDownloadUrl(semester, format) {
  const cleanSem = String(semester).toLowerCase().replace('th', '').replace('rd', '');
  return `/api/v1/timetable/${cleanSem}rd/${format}/`;
}
