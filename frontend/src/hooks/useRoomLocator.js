import { useState, useEffect } from 'react';
import { searchRooms, getRoomStatus, getFreeRooms } from '../api/roomApi';

export function useRoomLocator() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedRoomStatus, setSelectedRoomStatus] = useState(null);
  const [freeRooms, setFreeRooms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Debounced Room Search (300ms)
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    const handler = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const results = await searchRooms(searchQuery.trim());
        setSearchResults(results || []);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(handler);
  }, [searchQuery]);

  const inspectRoom = async (roomNumber) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getRoomStatus(roomNumber);
      setSelectedRoomStatus(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchFreeRooms = async (type) => {
    setLoading(true);
    setError(null);
    try {
      const rooms = await getFreeRooms(type);
      setFreeRooms(rooms || []);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  return {
    searchQuery,
    setSearchQuery,
    searchResults,
    selectedRoomStatus,
    freeRooms,
    loading,
    error,
    inspectRoom,
    fetchFreeRooms,
    clearSelectedRoom: () => setSelectedRoomStatus(null),
  };
}
