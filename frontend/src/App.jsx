import React, { useState } from 'react';
import { useStudentState } from './hooks/useStudentState';
import { Navbar } from './components/common/Navbar';
import { BottomNav } from './components/common/BottomNav';
import { StudentContextModal } from './components/student/StudentContextModal';
import { DashboardPage } from './pages/DashboardPage';
import { TimetablePage } from './pages/TimetablePage';
import { RoomsPage } from './pages/RoomsPage';
import { TeachersPage } from './pages/TeachersPage';
import { MorePage } from './pages/MorePage';
import { AdminDashboard } from './admin/AdminDashboard';

export function App() {
  const {
    context,
    state,
    loading,
    error,
    lastUpdated,
    refreshState,
    saveContext,
  } = useStudentState();

  const [activeTab, setActiveTab] = useState('home');
  const [isContextModalOpen, setIsContextModalOpen] = useState(false);
  const [inspectedRoom, setInspectedRoom] = useState(null);

  // If no student context is saved, show onboarding modal
  const showOnboarding = !context || isContextModalOpen;

  const handleGoToRoom = (roomNumber) => {
    setInspectedRoom(roomNumber);
    setActiveTab('rooms');
  };

  return (
    <div>
      <Navbar
        context={context}
        onOpenContextModal={() => setIsContextModalOpen(true)}
        onRefresh={refreshState}
        loading={loading}
        lastUpdated={lastUpdated}
      />

      <main className="app-container">
        {showOnboarding && (
          <StudentContextModal
            isOpen={true}
            onClose={context ? () => setIsContextModalOpen(false) : null}
            onSave={(newCtx) => {
              saveContext(newCtx);
              setIsContextModalOpen(false);
            }}
            currentContext={context}
          />
        )}

        {context && activeTab === 'home' && (
          <DashboardPage
            state={state}
            loading={loading}
            error={error}
            onRefresh={refreshState}
            onNavigateTab={setActiveTab}
            onInspectRoom={handleGoToRoom}
          />
        )}

        {context && activeTab === 'timetable' && (
          <TimetablePage context={context} />
        )}

        {context && activeTab === 'rooms' && (
          <RoomsPage initialRoom={inspectedRoom} />
        )}

        {context && activeTab === 'teachers' && (
          <TeachersPage />
        )}

        {activeTab === 'admin' && (
          <AdminDashboard />
        )}

        {context && activeTab === 'more' && (
          <MorePage
            context={context}
            onOpenContextModal={() => setIsContextModalOpen(true)}
            serverTime={state?.server_time}
          />
        )}
      </main>

      <BottomNav activeTab={activeTab} setActiveTab={setActiveTab} />
    </div>
  );
}

export default App;
