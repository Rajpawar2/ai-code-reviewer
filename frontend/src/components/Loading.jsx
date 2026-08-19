import React from 'react';
import { Loader2 } from 'lucide-react';

const Loading = ({ message = 'Analyzing code with AST, Ruff, Bandit, Radon & Ollama...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 space-y-4">
      <div className="relative">
        <div className="w-14 h-14 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-6 h-6 rounded-full bg-indigo-600/30 blur-sm"></div>
        </div>
      </div>
      <p className="text-sm font-medium text-gray-300 text-center max-w-sm">{message}</p>
    </div>
  );
};

export default Loading;
