import React from 'react';
import { CheckCircle, Clock, AlertCircle } from 'lucide-react';

interface ProcessingStatusProps {
  status: string;
}

export function ProcessingStatus({ status }: ProcessingStatusProps) {
  const steps = [
    { id: 'parsing', title: 'Document Parsing', description: 'Extracting text and structure' },
    { id: 'processing', title: 'Data Processing', description: 'Analyzing content and parameters' },
    { id: 'rules', title: 'Rule Processing', description: 'Checking compliance requirements' },
    { id: 'report', title: 'Report Generation', description: 'Creating compliance report' },
    { id: 'complete', title: 'Complete', description: 'Processing finished successfully' }
  ];

  const getStepStatus = (stepId: string) => {
    const currentIndex = steps.findIndex(s => s.id === status);
    const stepIndex = steps.findIndex(s => s.id === stepId);

    // special case → if we're on the last step and status is "complete", mark it completed
    if (status === 'complete' && stepId === 'complete') {
      return 'completed';
    }

    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'current';
    return 'pending';
  };

  const getIcon = (stepStatus: string) => {
    switch (stepStatus) {
      case 'completed': return <CheckCircle className="h-6 w-6 text-green-600" />;
      case 'current': return <Clock className="h-6 w-6 text-blue-600 animate-spin" />;
      default: return <AlertCircle className="h-6 w-6 text-gray-400" />;
    }
  };

  const getProgressPercentage = () => {
    const currentIndex = steps.findIndex(s => s.id === status);
    return ((currentIndex + 1) / steps.length) * 100;
  };

  return (
    <div>
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Processing Document</h2>
        <p className="text-gray-600 mt-2">Please wait while we analyze your document</p>
        
        <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${getProgressPercentage()}%` }}
          ></div>
        </div>
        <p className="text-sm text-gray-500 mt-2">{Math.round(getProgressPercentage())}% Complete</p>
      </div>

      <div className="space-y-4">
        {steps.map((step) => {
          const stepStatus = getStepStatus(step.id);
          return (
            <div
              key={step.id}
              className={`flex items-center p-4 rounded-lg border ${
                stepStatus === 'completed'
                  ? 'bg-green-50 border-green-200'
                  : stepStatus === 'current'
                  ? 'bg-blue-50 border-blue-200'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              {getIcon(stepStatus)}
              <div className="ml-4">
                <h3 className={`font-medium ${
                  stepStatus === 'completed' ? 'text-green-900' :
                  stepStatus === 'current' ? 'text-blue-900' : 'text-gray-500'
                }`}>
                  {step.title}
                </h3>
                <p className={`text-sm ${
                  stepStatus === 'completed' ? 'text-green-700' :
                  stepStatus === 'current' ? 'text-blue-700' : 'text-gray-500'
                }`}>
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}