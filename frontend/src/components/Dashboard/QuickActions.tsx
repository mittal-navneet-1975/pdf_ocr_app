import React from 'react';
import { Upload, FileText, Bell, TrendingUp, Shield } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface QuickActionsProps {
  onNavigate: (page: string) => void;
}

export function QuickActions({ onNavigate }: QuickActionsProps) {
  const { hasRole } = useAuth();

  const actions = [
    {
      id: 'upload',
      title: 'Upload Document',
      description: 'Start new compliance review',
      icon: Upload,
      color: 'bg-blue-500 hover:bg-blue-600'
    },
    {
      id: 'reports',
      title: 'View Reports',
      description: 'Browse compliance reports',
      icon: FileText,
      color: 'bg-green-500 hover:bg-green-600'
    },
    {
      id: 'alerts',
      title: 'Check Alerts',
      description: 'Review notifications',
      icon: Bell,
      color: 'bg-orange-500 hover:bg-orange-600'
    },
    {
      id: 'trends',
      title: 'Trend Analysis',
      description: 'View compliance trends',
      icon: TrendingUp,
      color: 'bg-purple-500 hover:bg-purple-600'
    },
    ...(hasRole(['admin']) ? [{
      id: 'audit',
      title: 'Audit Logs',
      description: 'Review system audit trail',
      icon: Shield,
      color: 'bg-red-500 hover:bg-red-600'
    }] : [])
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <button
              key={action.id}
              onClick={() => onNavigate(action.id)}
              className={`p-4 rounded-lg text-white transition-colors duration-200 ${action.color} text-center hover:scale-105 transform transition-transform duration-200`}
            >
              <Icon className="h-8 w-8 mx-auto mb-2" />
              <h4 className="font-medium text-sm">{action.title}</h4>
              <p className="text-xs opacity-90 mt-1">{action.description}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}