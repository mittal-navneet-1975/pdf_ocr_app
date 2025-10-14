import React, { useEffect, useState } from 'react';
import { CheckCircle, FileText } from 'lucide-react';

interface UploadConfirmationProps {
  reportId: string;
  fileName: string;
  outputs?: string[];
  onStartNew: () => void;
}

function unescapeHtmlEntities(html: string): string {
  const txt = document.createElement('textarea');
  txt.innerHTML = html;
  return txt.value;
}

export function UploadConfirmation({
  reportId,
  fileName,
  outputs = [],
  onStartNew,
}: UploadConfirmationProps) {
  const [reportHtml, setReportHtml] = useState<string | null>(null);
  const [complianceStatus, setComplianceStatus] = useState<string>('Loading...');

  useEffect(() => {
    const htmlFile = outputs.find((o) => o.endsWith('.html'));
    if (!htmlFile) return;

    // Use relative API path for Vercel deployment
    fetch(`http://pdf-ocr-backend-one.vercel.app/output/${encodeURIComponent(htmlFile)}`)
      .then((res) => res.text())
      .then((rawHtml) => {
        let html = rawHtml;

        // If escaped, unescape it
        try {
          html = JSON.parse(html);
        } catch {
          // not JSON encoded, skip
        }

        html = unescapeHtmlEntities(html);

        // Optional cleanup
        html = html.replace(/\\r\\n|\\n|\\r/g, '');

        // Save to render
        setReportHtml(html);

        // Extract compliance status from HTML
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        const h3 = doc.querySelector('h3');
        const text = h3?.textContent?.toLowerCase() || '';

        if (text.includes('non-compliance') || text.includes('non compliant')) {
          setComplianceStatus('Non-Compliant');
        } else if (text.includes('compliant')) {
          setComplianceStatus('Compliant');
        } else {
          setComplianceStatus('Unknown');
        }
      })
      .catch((err) => {
        console.error('Error fetching report:', err);
        setComplianceStatus('Error loading report');
      });
  }, [outputs]);

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
        {reportHtml ? (
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
                background-color: #fee;
              }
              .report-container small {
                font-size: 12px;
                display: block;
                margin-top: 4px;
              }
            `}</style>
            <div 
              className="report-container"
              dangerouslySetInnerHTML={{ __html: reportHtml }}
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