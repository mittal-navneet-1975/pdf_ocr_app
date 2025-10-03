import React, { useState } from 'react';
import { Bell, AlertTriangle, CheckCircle, Clock, Eye } from 'lucide-react';
import { Alert } from '../../types';

export function AlertsModule() {
  const [statusFilter, setStatusFilter] = useState('all');

  const mockAlerts: Alert[] = [
    {
      id: 'ALT-001',
      reportId: 'RPT-002',
      message: 'High severity compliance violation detected in pharma_product_data.pdf',
      severity: 'high',
      status: 'pending',
      createdAt: '2024-01-15T14:30:00Z'
    },
    {
      id: 'ALT-002',
      reportId: 'RPT-004',
      message: 'Missing required documentation in medical device report',
      severity: 'medium',
      status: 'acknowledged',
      createdAt: '2024-01-15T12:15:00Z'
    },
    {
      id: 'ALT-003',
      reportId: 'RPT-005',
      message: 'Minor formatting issues found in compliance report',
      severity: 'low',
      status: 'pending',
      createdAt: '2024-01-15T09:45:00Z'
    },
    {
      id: 'ALT-004',
      reportId: 'RPT-001',
      message: 'Compliance review completed successfully with warnings',
      severity: 'low',
      status: 'acknowledged',
      createdAt: '2024-01-14T16:20:00Z'
    }
  ];

  const filteredAlerts = mockAlerts.filter(alert => {
    return statusFilter === 'all' || alert.status === statusFilter;
  });

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'high':
        return <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">🔴 High</span>;
      case 'medium':
        return <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800">🟡 Medium</span>;
      case 'low':
        return <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">🔵 Low</span>;
      default:
        return <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">Unknown</span>;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'acknowledged':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-600" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
    }
  };

  const handleAcknowledge = (alertId: string) => {
    console.log('Acknowledging alert:', alertId);
    // Update alert status
  };

  const pendingCount = mockAlerts.filter(alert => alert.status === 'pending').length;
  const acknowledgedCount = mockAlerts.filter(alert => alert.status === 'acknowledged').length;

  return (
    <div className="space-y-6">
      {/* Alert Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="rounded-lg p-3 bg-red-50">
              <Bell className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">{mockAlerts.length}</p>
              <p className="text-sm font-medium text-gray-600">Total Alerts</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="rounded-lg p-3 bg-yellow-50">
              <Clock className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">{pendingCount}</p>
              <p className="text-sm font-medium text-gray-600">Pending Review</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="rounded-lg p-3 bg-green-50">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">{acknowledgedCount}</p>
              <p className="text-sm font-medium text-gray-600">Acknowledged</p>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b border-gray-200">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 md:mb-0">Alert Notifications</h2>
            
            <div className="flex space-x-4">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Alerts</option>
                <option value="pending">Pending</option>
                <option value="acknowledged">Acknowledged</option>
              </select>
            </div>
          </div>
        </div>

        <div className="divide-y divide-gray-200">
          {filteredAlerts.map((alert) => (
            <div key={alert.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 pt-1">
                  {getStatusIcon(alert.status)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    {getSeverityBadge(alert.severity)}
                    <span className="text-sm text-gray-500">Report: {alert.reportId}</span>
                  </div>
                  
                  <p className="text-sm text-gray-900 mb-2">{alert.message}</p>
                  
                  <p className="text-xs text-gray-500">
                    {new Date(alert.createdAt).toLocaleString()}
                  </p>
                </div>
                
                <div className="flex-shrink-0 flex space-x-2">
                  <button className="text-blue-600 hover:text-blue-900">
                    <Eye className="h-4 w-4" />
                  </button>
                  
                  {alert.status === 'pending' && (
                    <button
                      onClick={() => handleAcknowledge(alert.id)}
                      className="px-3 py-1 text-xs font-medium text-green-700 bg-green-100 rounded-full hover:bg-green-200"
                    >
                      Acknowledge
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}