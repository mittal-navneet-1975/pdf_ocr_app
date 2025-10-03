import React, { useEffect, useState } from 'react';
import { CheckCircle, FileText, ExternalLink } from 'lucide-react';

interface UploadConfirmationProps {
  reportId: string;
  fileName: string;
  outputs?: string[];
  onStartNew: () => void;
}

export function UploadConfirmation({ reportId, fileName, outputs = [], onStartNew }: UploadConfirmationProps) {
  const [complianceStatus, setComplianceStatus] = useState<string>('Loading...');
  const [statusColor, setStatusColor] = useState<string>('text-gray-600');

  useEffect(() => {
    const htmlFile = outputs.find(o => o.endsWith('.html'));
    if (!htmlFile) {
      setComplianceStatus('Unknown');
      setStatusColor('text-gray-600');
      return;
    }

    let aborted = false;

    fetch(`http://localhost:8000/output/${encodeURIComponent(htmlFile)}`)
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const html = await res.text();
        if (aborted) return;
        const status = extractComplianceStatus(html);
        setComplianceStatus(status ?? 'Unknown');
        setStatusColor(determineColor(status));
      })
      .catch((err) => {
        console.error('Failed to fetch report for status extraction', err);
        setComplianceStatus('Error loading status');
        setStatusColor('text-red-600');
      });

    return () => { aborted = true; };
  }, [outputs]);

  // Tries multiple methods to locate the compliance text in the HTML:
  // 1) common selectors (#compliance-status, .compliance-status, data attributes)
  // 2) meta tag <meta name="compliance-status" content="...">
  // 3) fallback: regex search inside the document body for keywords like "Compliant", "Non-Compliant", "Pass", "Fail"
  function extractComplianceStatus(html: string): string | null {
    try {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');

      // 1) check a few likely selectors
      const selectors = [
        '#compliance-status',
        '.compliance-status',
        '[data-compliance-status]',
        '#status',
        '.status',
        '[data-status]'
      ];
      for (const sel of selectors) {
        const el = doc.querySelector(sel);
        if (el && el.textContent?.trim()) {
          const t = el.textContent.trim();
          const normalized = normalizeStatusText(t);
          if (normalized) return normalized;
        }
      }

      // 2) meta tag
      const meta = doc.querySelector('meta[name="compliance-status"]') as HTMLMetaElement | null;
      if (meta && meta.content) {
        const normalized = normalizeStatusText(meta.content);
        if (normalized) return normalized;
      }

      // 3) fallback: search entire body text for common keywords
      const bodyText = doc.body?.textContent ?? html;
      const keywordRegex = /\b(compliant|non[- ]?compliant|complies|does not comply|doesn't comply|pass(?:ed)?|fail(?:ed)?|conform(?:s|ed)?|nonconform)\b/i;
      const match = bodyText.match(keywordRegex);
      if (match) {
        return normalizeStatusText(match[0]);
      }

      return null;
    } catch (e) {
      console.error('Error parsing HTML for compliance status', e);
      return null;
    }
  }

  // Normalize many possible strings into "Compliant" / "Non-Compliant"
  function normalizeStatusText(raw: string): string | null {
    const s = raw.trim().toLowerCase();
    if (/compliant/.test(s) || /pass(ed)?/.test(s) || /conform/.test(s)) return 'Compliant';
    if (/non[- ]?compliant/.test(s) || /does not comply/.test(s) || /doesn't comply/.test(s) || /fail(ed)?/.test(s) || /nonconform/.test(s)) return 'Non-Compliant';
    return null;
  }

  function determineColor(status: string | null): string {
    if (!status) return 'text-gray-600';
    const s = status.toLowerCase();
    if (s.includes('compliant') || s.includes('pass')) return 'text-green-600';
    if (s.includes('non') || s.includes('fail') || s.includes("does not")) return 'text-red-600';
    return 'text-gray-600';
  }

  const htmlFile = outputs.find(o => o.endsWith('.html'));

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

        <div className="text-sm">
          <p className="text-gray-600">Status</p>
          <p className={`font-semibold ${statusColor}`}>{complianceStatus}</p>
        </div>
      </div>

      <div className="space-y-4">
        {htmlFile ? (
          <button
            onClick={() => window.open(`http://localhost:8000/output/${encodeURIComponent(htmlFile)}`, '_blank')}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center justify-center"
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            View Detailed Report
          </button>
        ) : (
          <button disabled className="w-full bg-gray-300 text-gray-600 py-3 px-4 rounded-lg">
            Report not available yet
          </button>
        )}

        <button onClick={onStartNew} className="w-full bg-gray-600 text-white py-3 px-4 rounded-lg hover:bg-gray-700 transition-colors duration-200">
          Upload Another Document
        </button>
      </div>
    </div>
  );
}
