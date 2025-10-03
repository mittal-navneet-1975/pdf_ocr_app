import React from 'react';
import { Upload, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';
import { DashboardStats as StatsType } from '../../types';

interface DashboardStatsProps {
  stats: StatsType;
}

export function DashboardStats({ stats }: DashboardStatsProps) {
  const statCards = [
    {
      title: 'Total Uploads',
      value: stats.totalUploads,
      icon: Upload,
      color: 'bg-blue-50 text-blue-700',
      iconColor: 'text-blue-600'
    },
    {
      title: 'Compliant Reports',
      value: stats.compliantReports,
      icon: CheckCircle,
      color: 'bg-green-50 text-green-700',
      iconColor: 'text-green-600'
    },
    {
      title: 'Non-Compliant',
      value: stats.nonCompliantReports,
      icon: XCircle,
      color: 'bg-red-50 text-red-700',
      iconColor: 'text-red-600'
    },
    {
      title: 'Pending Review',
      value: stats.pendingReports,
      icon: Clock,
      color: 'bg-yellow-50 text-yellow-700',
      iconColor: 'text-yellow-600'
    },
    {
      title: 'Recent Alerts',
      value: stats.recentAlerts,
      icon: AlertTriangle,
      color: 'bg-orange-50 text-orange-700',
      iconColor: 'text-orange-600'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
      {statCards.map((card, index) => {
        const Icon = card.icon;
        return (
          <div key={index} className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow duration-200">
            <div className="flex items-center">
              <div className={`rounded-lg p-3 ${card.color}`}>
                <Icon className={`h-6 w-6 ${card.iconColor}`} />
              </div>
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                <p className="text-sm font-medium text-gray-600">{card.title}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}