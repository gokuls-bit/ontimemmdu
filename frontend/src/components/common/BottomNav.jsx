import React from 'react';
import { Home, Calendar, DoorOpen, Users, MoreHorizontal } from 'lucide-react';

export function BottomNav({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'timetable', label: 'Timetable', icon: Calendar },
    { id: 'rooms', label: 'Rooms', icon: DoorOpen },
    { id: 'teachers', label: 'Teachers', icon: Users },
    { id: 'more', label: 'More', icon: MoreHorizontal },
  ];

  return (
    <nav className="bottom-nav">
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = activeTab === item.id;
        return (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`nav-item ${isActive ? 'active' : ''}`}
          >
            <Icon size={20} />
            <span>{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
