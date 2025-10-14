import React, { useEffect, useState } from 'react';
import { CheckCircle, FileText } from 'lucide-react';

interface UploadConfirmationProps {
  reportId: string;
  fileName: string;
  htmlReport?: string;
  onStartNew: () => void;
}

export function UploadConfirmation({
  reportId,
  fileName,
  htmlReport,
  onStartNew,
}: UploadConfirmationProps) {
  const [complianceStatus, setComplianceStatus] = useState<string>('Loading...');

  useEffect(() => {
    if (!htmlReport) {
      setComplianceStatus('No report available');
      return;
    }

    try {
      // Extract compliance status from HTML
      const parser = new DOMParser();
      const doc = parser.parseFromString(htmlReport, 'text/html');

      const h3 = doc.querySelector('h3');
      const text = h3?.textContent?.toLowerCase() || '';

      if (text.includes('non-compliant') || text.includes('non compliant')) {
        setComplianceStatus('Non-Compliant');
      } else if (text.includes('compliant')) {
        setComplianceStatus('Compliant');
      } else {
        setComplianceStatus('Unknown');
      }
    } catch (err) {
      console.error('Error parsing report:', err);
      setComplianceStatus('Error parsing report');
    }
  }, [htmlReport]);

  return (
    <div className="text-center">
      <CheckCircle className="mx-auto h-16 w-16 text-green-600 mb-6" />
      <h2 className="text-3xl font-bold text-gray-900 mb-2">Upload Complete!</h2>
      <p className="text-gray-600 mb-8">Your document has been processed successfully</p>

      <div className="bg-gray-50 rounded-lg p-6 mb-8">
        <div className="flex items-center justify-center mb-4">
          <FileText className="h-8 w-8 text-blue-600 mr-3" />
          <div className="text-left">
            <p className="font-semibold text-gray-900">{fileName}</p>
            <p className="text-sm text-gray-600">Report ID: {reportId}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-600">Status</p>
            <p
              className={`font-semibold ${
                complianceStatus === 'Compliant'
                  ? 'text-green-600'
                  : complianceStatus === 'Non-Compliant'
                  ? 'text-red-600'
                  : 'text-gray-600'
              }`}
            >
              {complianceStatus}
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {htmlReport ? (
          <div className="border rounded-lg p-6 text-left bg-white max-h-[600px] overflow-auto">
            <style>{`
              .report-container h1 {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                color: #1f2937;
              }
              .report-container table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background: white;
              }
              .report-container table th {
                background-color: #f3f4f6;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                border: 1px solid #d1d5db;
                color: #374151;
              }
              .report-container table td {
                padding: 10px 12px;
                border: 1px solid #d1d5db;
                color: #1f2937;
              }
              .report-container table tr:nth-child(even) {
                background-color: #f9fafb;
              }
              .report-container table tr:hover {
                background-color: #f3f4f6;
              }
              .report-container h3 {
                font-size: 20px;
                font-weight: bold;
                margin-top: 20px;
                padding: 15px;
                border-radius: 8px;
              }
              .report-container h3[style*="color:green"] {
                background-color: #f0fdf4;
              }
              .report-container h3[style*="color:red"] {
                background-color: #fef2f2;
              }
              .report-container small {
                font-size: 12px;
                display: block;
                margin-top: 4px;
              }
            `}</style>
            <div 
              className="report-container"
              dangerouslySetInnerHTML={{ __html: htmlReport }}
            />
          </div>
        ) : (
          <p className="text-gray-500">Report not available yet...</p>
        )}

        <button
          onClick={onStartNew}
          className="w-full bg-gray-600 text-white py-3 px-4 rounded-lg hover:bg-gray-700 transition-colors duration-200"
        >
          Upload Another Document
        </button>
      </div>
    </div>
  );
}