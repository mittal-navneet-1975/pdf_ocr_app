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
  const [outputs, setOutputs] = useState<string[]>([]);

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
      setOutputs([]);
      setCurrentStep(4);
  
      setProcessingStatus('parsing');
  
      try {
        const formData = new FormData();
        formData.append('file', file);
  
        await new Promise((r) => setTimeout(r, 500));
  
        // Roll back to original backend endpoint
        const res = await fetch('http://pdf-ocr-backend-one.vercel.app/upload-pdf/', {
          method: 'POST',
          body: formData,
        });
        const data = await res.json();
        const receivedOutputs: string[] = data.outputs || [];
        setOutputs(receivedOutputs);
  
        setProcessingStatus('processing');
        setTimeout(() => setProcessingStatus('rules'), 1200);
        setTimeout(() => setProcessingStatus('report'), 2600);
        setTimeout(() => {
          setProcessingStatus('complete');
          setReportId('RPT-' + Date.now());
        }, 3800);
      } catch (err) {
        console.error('Upload error', err);
        setProcessingStatus('error');
      }
    };
  // ...existing code...

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
            <div className="mt-6 flex justify-center">
              <button
                onClick={() => {
                  // go to confirmation only when complete
                  if (processingStatus === 'complete') {
                    setCurrentStep(5);
                  }
                }}
                disabled={processingStatus !== 'complete'}
                className={`px-6 py-2 rounded-lg text-white ${processingStatus === 'complete' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-300 cursor-not-allowed'}`}
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
            outputs={outputs}
            onStartNew={() => {
              setCurrentStep(1);
              setSelectedProduct('');
              setSelectedVendor('');
              setUploadedFile(null);
              setProcessingStatus('');
              setReportId('');
              setOutputs([]);
            }}
          />
        )}
      </div>
    </div>
  );
}