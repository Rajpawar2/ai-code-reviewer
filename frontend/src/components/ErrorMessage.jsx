import React from 'react';
import { AlertTriangle, XCircle } from 'lucide-react';

const ErrorMessage = ({ error, onDismiss }) => {
  if (!error) return null;

  const getMessage = () => {
    if (typeof error === 'string') return error;
    if (error.response?.data?.error?.message) return error.response.data.error.message;
    if (error.response?.data?.detail) return error.response.data.detail;
    if (error.message) return error.message;
    return 'An unexpected error occurred.';
  };

  return (
    <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 flex items-start justify-between gap-3 text-rose-200 text-sm mb-6 shadow-lg shadow-rose-950/20 animate-fade-in">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold block mb-0.5">Error</span>
          <p className="text-rose-300 text-xs leading-relaxed">{getMessage()}</p>
        </div>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-rose-400 hover:text-rose-200 transition-colors"
        >
          <XCircle className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;
