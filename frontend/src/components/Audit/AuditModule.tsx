import React, { useState } from 'react';
import { Shield, Search, Download, Eye, Calendar, User } from 'lucide-react';
import { AuditLog } from '../../types';
import { useAuth } from '../../context/AuthContext';

export function AuditModule() {
  const { hasRole } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [actionFilter, setActionFilter] = useState('all');

  if (!hasRole(['admin'])) {
    return (
      <div className="text-center py-12">
        <Shield className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900">Access Restricted</h3>
        <p className="text-gray-600">Only administrators can access audit logs.</p>
      </div>
    );
  }

  const mockAuditLogs: AuditLog[] = [
    {
      id: 'AUD-001',
      userId: '1',
      userName: 'Admin User',
      action: 'LOGIN',
      details: 'User logged into the system',
      timestamp: '2024-01-15T14:30:00Z'
    },
    {
      id: 'AUD-002',
      userId: '2',
      userName: 'Operator User',
      action: 'UPLOAD_DOCUMENT',
      details: 'Uploaded document: medical_device_specs.pdf',
      timestamp: '2024-01-15T14:25:00Z',
      reportId: 'RPT-001'
    },
    {
      id: 'AUD-003',
      userId: '3',
      userName: 'Manager User',
      action: 'VIEW_REPORT',
      details: 'Viewed compliance report RPT-002',
      timestamp: '2024-01-15T14:20:00Z',
      reportId: 'RPT-002'
    },
    {
      id: 'AUD-004',
      userId: '1',
      userName: 'Admin User',
      action: 'ACKNOWLEDGE_ALERT',
      details: 'Acknowledged alert ALT-002',
      timestamp: '2024-01-15T14:15:00Z'
    },
    {
      id: 'AUD-005',
      userId: '2',
      userName: 'Operator User',
      action: 'EXPORT_DATA',
      details: 'Exported compliance report data to CSV',
      timestamp: '2024-01-15T14:10:00Z'
    },
    {
      id: 'AUD-006',
      userId: '3',
      userName: 'Manager User',
      action: 'UPDATE_USER_ROLE',
      details: 'Updated user role for john.doe@company.com',
      timestamp: '2024-01-15T14:05:00Z'
    }
  ];

  const filteredLogs = mockAuditLogs.filter(log => {
    const matchesSearch = log.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         log.details.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesAction = actionFilter === 'all' || log.action === actionFilter;
    return matchesSearch && matchesAction;
  });

  const getActionBadge = (action: string) => {
    const actionConfig = {
      'LOGIN': { color: 'bg-blue-100 text-blue-800', icon: User },
      'UPLOAD_DOCUMENT': { color: 'bg-green-100 text-green-800', icon: Shield },
      'VIEW_REPORT': { color: 'bg-gray-100 text-gray-800', icon: Eye },
      'ACKNOWLEDGE_ALERT': { color: 'bg-yellow-100 text-yellow-800', icon: Shield },
      'EXPORT_DATA': { color: 'bg-purple-100 text-purple-800', icon: Download },
      'UPDATE_USER_ROLE': { color: 'bg-red-100 text-red-800', icon: User }
    };

    const config = actionConfig[action as keyof typeof actionConfig] || { color: 'bg-gray-100 text-gray-800', icon: Shield };

    return (
      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${config.color}`}>
        {action.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Audit Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="rounded-lg p-3 bg-blue-50">
              <Shield className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">{mockAuditLogs.length}</p>
              <p className="text-sm font-medium text-gray-600">Total Events</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="rounded-lg p-3 bg-green-50">
              <User className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">3</p>
              <p className="text-sm font-medium text-gray-600">Active Users</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="rounded-lg p-3 bg-purple-50">
              <Calendar className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">24h</p>
              <p className="text-sm font-medium text-gray-600">Time Range</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="rounded-lg p-3 bg-yellow-50">
              <Download className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">2</p>
              <p className="text-sm font-medium text-gray-600">Exports Today</p>
            </div>
          </div>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b border-gray-200">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 md:mb-0">System Audit Logs</h2>
            
            <div className="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search logs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <select
                value={actionFilter}
                onChange={(e) => setActionFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Actions</option>
                <option value="LOGIN">Login Events</option>
                <option value="UPLOAD_DOCUMENT">Document Uploads</option>
                <option value="VIEW_REPORT">Report Views</option>
                <option value="EXPORT_DATA">Data Exports</option>
              </select>
              
              <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                <Download className="h-4 w-4 mr-2" />
                Export Audit Trail
              </button>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Details</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Report ID</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{log.userName}</div>
                    <div className="text-sm text-gray-500">ID: {log.userId}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getActionBadge(log.action)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                    {log.details}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {log.reportId || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}