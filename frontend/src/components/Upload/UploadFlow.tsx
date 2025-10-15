import React, { useState } from 'react';
import { ChevronRight } from 'lucide-react';
import { ProductSelection } from './ProductSelection';
import { VendorSelection } from './VendorSelection';
import FileUpload from './FileUpload';
import { ProcessingStatus } from './ProcessingStatus';
import { UploadConfirmation } from './UploadConfirmation';

export function UploadFlow() {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedProduct, setSelectedProduct] = useState<string>('');
  const [selectedVendor, setSelectedVendor] = useState<string>('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [processingStatus, setProcessingStatus] = useState<string>('');
  const [reportId, setReportId] = useState<string>('');
  const [htmlReport, setHtmlReport] = useState<string>('');
  const [error, setError] = useState<string>('');

  const steps = [
    { id: 1, title: 'Select Product', description: 'Choose the product category' },
    { id: 2, title: 'Select Vendor', description: 'Choose the vendor' },
    { id: 3, title: 'Upload Document', description: 'Upload PDF document' },
    { id: 4, title: 'Processing', description: 'Document analysis in progress' },
    { id: 5, title: 'Confirmation', description: 'Review results' }
  ];

  const handleNext = () => {
    if (currentStep < 5) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleFileUpload = async (file: File) => {
    setUploadedFile(file);
    setHtmlReport('');
    setError('');
    setCurrentStep(4);
    setProcessingStatus('parsing');

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Simulate parsing delay
      await new Promise((r) => setTimeout(r, 500));

      // Call backend
      const res = await fetch('https://pdf-ocr-backend-one.vercel.app/upload-pdf/', {
        method: 'POST',
        body: formData,
      });

      // Check if response is ok
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      
      // Log the response to debug
      console.log('Backend response:', data);
      
      // Check multiple possible response structures
      const report = data.htmlReport || data.html_report || data.report || data.html || '';
      
      if (!report) {
        console.warn('No HTML report found in response. Response keys:', Object.keys(data));
        throw new Error('No HTML report received from backend');
      }

      setHtmlReport(report);

      // Simulate processing steps
      setProcessingStatus('processing');
      await new Promise((r) => setTimeout(r, 1200));
      
      setProcessingStatus('rules');
      await new Promise((r) => setTimeout(r, 1400));
      
      setProcessingStatus('report');
      await new Promise((r) => setTimeout(r, 1200));
      
      setProcessingStatus('complete');
      setReportId('RPT-' + Date.now());

    } catch (err) {
      console.error('Upload error:', err);
      setProcessingStatus('error');
      setError(err instanceof Error ? err.message : 'An error occurred during upload');
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <React.Fragment key={step.id}>
              <div className={`flex flex-col items-center ${
                currentStep >= step.id ? 'text-blue-600' : 'text-gray-400'
              }`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${
                  currentStep >= step.id 
                    ? 'border-blue-600 bg-blue-600 text-white' 
                    : 'border-gray-300 text-gray-400'
                }`}>
                  {step.id}
                </div>
                <div className="mt-2 text-center">
                  <p className="text-sm font-medium">{step.title}</p>
                  <p className="text-xs text-gray-500">{step.description}</p>
                </div>
              </div>
              {index < steps.length - 1 && (
                <ChevronRight className="h-5 w-5 text-gray-400" />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg shadow-sm border p-8">
        {currentStep === 1 && (
          <ProductSelection
            selectedProduct={selectedProduct}
            onProductSelect={(productId) => {
              setSelectedProduct(productId);
              handleNext();
            }}
          />
        )}

        {currentStep === 2 && (
          <VendorSelection
            productId={selectedProduct}
            selectedVendor={selectedVendor}
            onVendorSelect={(vendorId) => {
              setSelectedVendor(vendorId);
              handleNext();
            }}
            onBack={handleBack}
          />
        )}

        {currentStep === 3 && (
          <FileUpload
            onFileUpload={handleFileUpload}
            onBack={handleBack}
          />
        )}

        {currentStep === 4 && (
          <div>
            <ProcessingStatus status={processingStatus} />
            
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600 text-sm">{error}</p>
                <button
                  onClick={handleBack}
                  className="mt-2 text-sm text-red-700 underline"
                >
                  Go back and try again
                </button>
              </div>
            )}

            <div className="mt-6 flex justify-center gap-4">
              {processingStatus === 'error' && (
                <button
                  onClick={handleBack}
                  className="px-6 py-2 rounded-lg bg-gray-500 text-white hover:bg-gray-600"
                >
                  Try Again
                </button>
              )}
              <button
                onClick={() => {
                  if (processingStatus === 'complete') {
                    setCurrentStep(5);
                  }
                }}
                disabled={processingStatus !== 'complete'}
                className={`px-6 py-2 rounded-lg text-white ${
                  processingStatus === 'complete' 
                    ? 'bg-blue-600 hover:bg-blue-700' 
                    : 'bg-gray-300 cursor-not-allowed'
                }`}
              >
                View Results
              </button>
            </div>
          </div>
        )}

        {currentStep === 5 && (
          <UploadConfirmation
            reportId={reportId}
            fileName={uploadedFile?.name || ''}
            htmlReport={htmlReport}
            onStartNew={() => {
              setCurrentStep(1);
              setSelectedProduct('');
              setSelectedVendor('');
              setUploadedFile(null);
              setProcessingStatus('');
              setReportId('');
              setHtmlReport('');
              setError('');
            }}
          />
        )}
      </div>
    </div>
  );
}