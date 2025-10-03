import React, { useRef, useState } from "react";

interface FileUploadProps {
  onFileUpload: (file: File) => void;
  onBack?: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload, onBack }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleIconClick = () => {
    fileInputRef.current?.click();
  };

  const handleStartProcessing = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (selectedFile) {
      onFileUpload(selectedFile);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center py-8">
      <h2 className="text-xl font-semibold mb-4">Upload PDF</h2>
      <div className="flex flex-col items-center">
        <button
          type="button"
          onClick={handleIconClick}
          className="w-24 h-24 rounded-full bg-blue-100 hover:bg-blue-200 flex items-center justify-center mb-3 border-2 border-dashed border-blue-400 focus:outline-none"
          aria-label="Upload PDF"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
        </button>
        <input
          ref={fileInputRef}
          id="pdf-upload"
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          className="hidden"
        />
        <div className="mb-2 text-gray-700 min-h-[1.5rem]">
          {selectedFile ? selectedFile.name : "No file selected"}
        </div>
        <button
          onClick={handleStartProcessing}
          disabled={!selectedFile}
          className={`mt-2 px-6 py-2 rounded bg-blue-600 text-white font-semibold shadow hover:bg-blue-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed`}
        >
          Start Processing
        </button>
        {onBack && (
          <button
            onClick={onBack}
            className="mt-2 px-4 py-2 rounded bg-gray-300 text-gray-700 hover:bg-gray-400"
          >
            Back
          </button>
        )}
      </div>
    </div>
  );
};

export default FileUpload;