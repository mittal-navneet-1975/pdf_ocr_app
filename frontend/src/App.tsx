import { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginForm } from './components/Auth/LoginForm';
import { Navbar } from './components/Layout/Navbar';
import { Sidebar } from './components/Layout/Sidebar';
import { DashboardStats } from './components/Dashboard/DashboardStats';
import { QuickActions } from './components/Dashboard/QuickActions';
import { UploadFlow } from './components/Upload/UploadFlow';
import { ReportsModule } from './components/Reports/ReportsModule';
import { AlertsModule } from './components/Alerts/AlertsModule';
import { TrendsModule } from './components/Trends/TrendsModule';
import { AuditModule } from './components/Audit/AuditModule';

function Dashboard({ onNavigate }: { onNavigate: (page: string) => void }) {
  const mockStats = {
    totalUploads: 1247,
    compliantReports: 1089,
    nonCompliantReports: 158,
    pendingReports: 42,
    recentAlerts: 7
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Monitor compliance status and system activity</p>
      </div>
      
      <DashboardStats stats={mockStats} />
      
      <QuickActions onNavigate={onNavigate} />
    </div>
  );
}

function AppContent() {
  const { user } = useAuth();
  const [currentPage, setCurrentPage] = useState('dashboard');

  if (!user) {
    return <LoginForm />;
  }

  const renderContent = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard onNavigate={setCurrentPage} />;
      case 'upload':
        return <UploadFlow />;
      case 'reports':
        return <ReportsModule />;
      case 'alerts':
        return <AlertsModule />;
      case 'trends':
        return <TrendsModule />;
      case 'audit':
        return <AuditModule />;
      default:
        return <Dashboard onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar currentPage={currentPage} onPageChange={setCurrentPage} />
        <main className="flex-1 p-8">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;