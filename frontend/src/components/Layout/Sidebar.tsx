import React from 'react';
import { 
  Home, 
  Upload, 
  FileText, 
  Bell, 
  TrendingUp, 
  Shield,
  ChevronRight
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  currentPage: string;
  onPageChange: (page: string) => void;
}

export function Sidebar({ currentPage, onPageChange }: SidebarProps) {
  const { hasRole } = useAuth();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'upload', label: 'Upload Flow', icon: Upload },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'alerts', label: 'Alerts', icon: Bell },
    { id: 'trends', label: 'Trend Analysis', icon: TrendingUp },
    ...(hasRole(['admin']) ? [{ id: 'audit', label: 'Audit Logs', icon: Shield }] : [])
  ];

  return (
    <div className="bg-white w-64 shadow-sm h-full">
      <nav className="mt-8">
        <div className="px-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => onPageChange(item.id)}
                className={`w-full group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150 ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className={`mr-3 h-5 w-5 ${isActive ? 'text-blue-700' : 'text-gray-400 group-hover:text-gray-500'}`} />
                {item.label}
                {isActive && <ChevronRight className="ml-auto h-4 w-4" />}
              </button>
            );
          })}
        </div>
      </nav>
    </div>
  );
}