import React, { useState } from 'react';
import { RoomLocator } from '../components/rooms/RoomLocator';
import { FreeRoomFinder } from '../components/rooms/FreeRoomFinder';
import { useRoomLocator } from '../hooks/useRoomLocator';
import { Search, DoorOpen } from 'lucide-react';

export function RoomsPage({ initialRoom }) {
  const [activeTab, setActiveTab] = useState('free');
  const roomLocator = useRoomLocator();

  React.useEffect(() => {
    if (initialRoom) {
      setActiveTab('locator');
      roomLocator.inspectRoom(initialRoom);
    }
  }, [initialRoom]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Sub Tabs: LOCATE ROOM vs FREE ROOMS NOW */}
      <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(0,0,0,0.2)', padding: '0.25rem', borderRadius: '12px' }}>
        <button
          onClick={() => setActiveTab('free')}
          style={{
            flex: 1,
            padding: '0.65rem',
            borderRadius: '10px',
            fontWeight: 700,
            fontSize: '0.85rem',
            cursor: 'pointer',
            border: 'none',
            background: activeTab === 'free' ? 'rgba(99, 102, 241, 0.25)' : 'transparent',
            color: activeTab === 'free' ? '#a78bfa' : 'var(--text-secondary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.4rem',
          }}
        >
          <DoorOpen size={16} /> FREE ROOMS NOW
        </button>

        <button
          onClick={() => setActiveTab('locator')}
          style={{
            flex: 1,
            padding: '0.65rem',
            borderRadius: '10px',
            fontWeight: 700,
            fontSize: '0.85rem',
            cursor: 'pointer',
            border: 'none',
            background: activeTab === 'locator' ? 'rgba(99, 102, 241, 0.25)' : 'transparent',
            color: activeTab === 'locator' ? '#a78bfa' : 'var(--text-secondary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.4rem',
          }}
        >
          <Search size={16} /> SEARCH ROOM
        </button>
      </div>

      {activeTab === 'free' ? (
        <FreeRoomFinder
          onSelectRoom={(r) => {
            setActiveTab('locator');
            roomLocator.inspectRoom(r);
          }}
        />
      ) : (
        <RoomLocator {...roomLocator} />
      )}
    </div>
  );
}
