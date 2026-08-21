import React from 'react';

export function StatusBadge({ status }) {
  if (!status) return null;

  const normalized = String(status).toLowerCase().replace(/\s+/g, '_');
  let label = String(status).toUpperCase();

  if (normalized === 'active_class' || normalized === 'current') {
    label = '● ACTIVE CLASS';
  } else if (normalized === 'free') {
    label = '✓ FREE';
  } else if (normalized === 'occupied' || normalized === 'busy') {
    label = '● OCCUPIED';
  } else if (normalized === 'cancelled') {
    label = '✕ CANCELLED';
  } else if (normalized === 'lunch' || normalized === 'break') {
    label = '☕ ' + label;
  }

  return (
    <span className={`status-pill status-${normalized}`}>
      {label}
    </span>
  );
}
