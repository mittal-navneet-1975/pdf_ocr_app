import React, { useState } from 'react';
import { TrendingUp, Calendar, Filter, Download, BarChart3 } from 'lucide-react';

export function TrendsModule() {
  const [dateRange, setDateRange] = useState('30d');
  const [productFilter, setProductFilter] = useState('all');

  // Mock trend data
  const trendData = [
    { month: 'Jan', compliant: 85, nonCompliant: 15, total: 100 },
    { month: 'Feb', compliant: 78, nonCompliant: 22, total: 100 },
    { month: 'Mar', compliant: 92, nonCompliant: 8, total: 100 },
    { month: 'Apr', compliant: 88, nonCompliant: 12, total: 100 },
    { month: 'May', compliant: 95, nonCompliant: 5, total: 100 },
    { month: 'Jun', compliant: 83, nonCompliant: 17, total: 100 }
  ];

  const complianceRate = trendData[trendData.length - 1].compliant;
  const trend = complianceRate > trendData[trendData.length - 2].compliant ? 'up' : 'down';

  return (
    <div className="space-y-6">
      {/* Trend Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="rounded-lg p-3 bg-blue-50">
              <TrendingUp className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">{complianceRate}%</p>
              <p className="text-sm font-medium text-gray-600">Compliance Rate</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="rounded-lg p-3 bg-green-50">
              <BarChart3 className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">+5.2%</p>
              <p className="text-sm font-medium text-gray-600">Month over Month</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="rounded-lg p-3 bg-purple-50">
              <Calendar className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">486</p>
              <p className="text-sm font-medium text-gray-600">Total Reviews</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="rounded-lg p-3 bg-yellow-50">
              <TrendingUp className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">2.1 days</p>
              <p className="text-sm font-medium text-gray-600">Avg. Review Time</p>
            </div>
          </div>
        </div>
      </div>

      {/* Chart Section */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b border-gray-200">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 md:mb-0">Compliance Trends</h2>
            
            <div className="flex space-x-4">
              <select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
                <option value="1y">Last Year</option>
              </select>
              
              <select
                value={productFilter}
                onChange={(e) => setProductFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Products</option>
                <option value="medical">Medical Devices</option>
                <option value="pharma">Pharmaceutical</option>
                <option value="food">Food & Beverages</option>
                <option value="cosmetics">Cosmetics</option>
              </select>
              
              <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                <Download className="h-4 w-4 mr-2" />
                Export Chart
              </button>
            </div>
          </div>
        </div>

        <div className="p-6">
          {/* Simple Chart Visualization */}
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
              <span>Compliance Rate Over Time</span>
              <div className="flex space-x-4">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded mr-2"></div>
                  <span>Compliant</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-red-500 rounded mr-2"></div>
                  <span>Non-Compliant</span>
                </div>
              </div>
            </div>
            
            {/* Chart Bars */}
            <div className="space-y-3">
              {trendData.map((data, index) => (
                <div key={index} className="flex items-center space-x-4">
                  <div className="w-12 text-sm text-gray-600">{data.month}</div>
                  <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
                    <div 
                      className="bg-green-500 h-6 rounded-full flex items-center justify-end pr-2"
                      style={{ width: `${data.compliant}%` }}
                    >
                      <span className="text-white text-xs font-medium">{data.compliant}%</span>
                    </div>
                    <div 
                      className="bg-red-500 h-6 rounded-r-full absolute top-0 right-0 flex items-center justify-end pr-2"
                      style={{ width: `${data.nonCompliant}%` }}
                    >
                      <span className="text-white text-xs font-medium">{data.nonCompliant}%</span>
                    </div>
                  </div>
                  <div className="w-16 text-sm text-gray-600">{data.total} reports</div>
                </div>
              ))}
            </div>
          </div>

          {/* Key Insights */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="text-sm font-medium text-green-800">Best Performing Category</p>
                <p className="text-lg font-bold text-green-900">Medical Devices</p>
                <p className="text-xs text-green-700">97% compliance rate</p>
              </div>
              
              <div className="p-4 bg-yellow-50 rounded-lg">
                <p className="text-sm font-medium text-yellow-800">Needs Attention</p>
                <p className="text-lg font-bold text-yellow-900">Chemical Products</p>
                <p className="text-xs text-yellow-700">72% compliance rate</p>
              </div>
              
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm font-medium text-blue-800">Trending</p>
                <p className="text-lg font-bold text-blue-900">+12% This Month</p>
                <p className="text-xs text-blue-700">Overall improvement</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}