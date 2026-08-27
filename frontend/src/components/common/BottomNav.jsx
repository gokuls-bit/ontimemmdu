import React from 'react';
import { Home, Calendar, DoorOpen, Users, Shield, MoreHorizontal } from 'lucide-react';

export function BottomNav({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'timetable', label: 'Schedule', icon: Calendar },
    { id: 'rooms', label: 'Rooms', icon: DoorOpen },
    { id: 'teachers', label: 'Faculty', icon: Users },
    { id: 'admin', label: 'Admin', icon: Shield },
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
            <Icon size={19} />
            <span>{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
