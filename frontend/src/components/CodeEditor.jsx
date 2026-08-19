import React, { Suspense, lazy } from 'react';
import { Copy, Check } from 'lucide-react';

const Monaco = lazy(() => import('@monaco-editor/react'));

const CodeEditor = ({ 
  value, 
  onChange, 
  language = 'python', 
  readOnly = false, 
  height = '400px',
  title = 'Code Editor',
  showCopy = true
}) => {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="border border-gray-800 rounded-2xl overflow-hidden bg-[#0F1422] shadow-xl">
      {/* Editor Header Bar */}
      <div className="px-4 py-2.5 bg-[#141A29] border-b border-gray-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <span className="w-3 h-3 rounded-full bg-red-500/60 inline-block"></span>
            <span className="w-3 h-3 rounded-full bg-yellow-500/60 inline-block"></span>
            <span className="w-3 h-3 rounded-full bg-emerald-500/60 inline-block"></span>
          </div>
          <span className="text-xs font-mono text-gray-400 ml-2">{title}</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">
            {language}
          </span>
          {showCopy && value && (
            <button
              onClick={handleCopy}
              className="text-xs flex items-center gap-1 text-gray-400 hover:text-white bg-gray-800 hover:bg-gray-700 px-2.5 py-1 rounded-md border border-gray-700 transition-colors"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? 'Copied' : 'Copy Code'}
            </button>
          )}
        </div>
      </div>

      {/* Editor Area */}
      <div style={{ height }}>
        <Suspense fallback={
          <div className="h-full flex items-center justify-center text-gray-500 font-mono text-sm">
            Loading editor...
          </div>
        }>
          <Monaco
            height="100%"
            language={language}
            theme="vs-dark"
            value={value}
            onChange={onChange}
            options={{
              readOnly,
              minimap: { enabled: false },
              fontSize: 13,
              fontFamily: "'JetBrains Mono', monospace",
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 4,
              padding: { top: 12, bottom: 12 },
              lineNumbersMinChars: 3,
            }}
          />
        </Suspense>
      </div>
    </div>
  );
};

export default CodeEditor;
