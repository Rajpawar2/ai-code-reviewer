import React, { useState } from 'react';
import { 
  AlertCircle, 
  AlertTriangle, 
  Info, 
  ShieldAlert, 
  CheckCircle2, 
  ChevronDown, 
  ChevronUp, 
  Copy, 
  Check 
} from 'lucide-react';

const FindingCard = ({ finding }) => {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case 'CRITICAL':
        return {
          badge: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
          icon: <ShieldAlert className="w-4 h-4 text-rose-400" />
        };
      case 'HIGH':
        return {
          badge: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
          icon: <AlertTriangle className="w-4 h-4 text-amber-400" />
        };
      case 'MEDIUM':
        return {
          badge: 'bg-blue-500/15 text-blue-300 border-blue-500/30',
          icon: <AlertCircle className="w-4 h-4 text-blue-400" />
        };
      case 'LOW':
      default:
        return {
          badge: 'bg-slate-500/15 text-slate-300 border-slate-500/30',
          icon: <Info className="w-4 h-4 text-slate-400" />
        };
    }
  };

  const getCategoryBadge = (cat) => {
    const map = {
      security: 'bg-red-950/40 text-red-400 border-red-800/40',
      bug: 'bg-rose-950/40 text-rose-400 border-rose-800/40',
      performance: 'bg-yellow-950/40 text-yellow-400 border-yellow-800/40',
      complexity: 'bg-purple-950/40 text-purple-400 border-purple-800/40',
      maintainability: 'bg-teal-950/40 text-teal-400 border-teal-800/40',
      ast: 'bg-indigo-950/40 text-indigo-400 border-indigo-800/40',
      lint: 'bg-blue-950/40 text-blue-400 border-blue-800/40',
      quality: 'bg-cyan-950/40 text-cyan-400 border-cyan-800/40',
    };
    return map[cat.toLowerCase()] || 'bg-gray-800 text-gray-300 border-gray-700';
  };

  const { badge, icon } = getSeverityBadge(finding.severity);

  const handleCopy = () => {
    if (finding.suggested_code) {
      navigator.clipboard.writeText(finding.suggested_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="bg-[#111827] border border-gray-800/80 rounded-xl overflow-hidden hover:border-gray-700 transition-all shadow-md">
      <div 
        onClick={() => setExpanded(!expanded)}
        className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-800/30 transition-colors"
      >
        <div className="flex items-center gap-3 flex-1 min-w-0 pr-4">
          <div className="flex-shrink-0">{icon}</div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${badge}`}>
                {finding.severity}
              </span>
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium border ${getCategoryBadge(finding.category)}`}>
                {finding.category}
              </span>
              {finding.line_number > 0 && (
                <span className="text-xs px-2 py-0.5 rounded-md bg-gray-800 text-gray-400 border border-gray-700 font-mono">
                  Line {finding.line_number}
                </span>
              )}
            </div>
            <h4 className="text-sm font-semibold text-white truncate">{finding.title}</h4>
          </div>
        </div>

        <button 
          type="button" 
          aria-label={expanded ? "Collapse details" : "Expand details"}
          className="p-1 rounded-lg text-gray-400 hover:text-white"
        >
          {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>
      </div>

      {expanded && (
        <div className="p-4 pt-0 border-t border-gray-800/60 bg-gray-900/40 text-sm space-y-3">
          <div className="pt-3">
            <h5 className="text-xs font-semibold uppercase text-gray-400 tracking-wider mb-1">Description</h5>
            <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{finding.description}</p>
          </div>

          {finding.recommendation && (
            <div className="p-3 rounded-lg bg-indigo-950/20 border border-indigo-900/30">
              <h5 className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" /> Recommendation
              </h5>
              <p className="text-indigo-200 text-xs leading-relaxed">{finding.recommendation}</p>
            </div>
          )}

          {finding.suggested_code && (
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Suggested Fix</span>
                <button
                  onClick={handleCopy}
                  className="text-xs flex items-center gap-1 text-gray-400 hover:text-white bg-gray-800 px-2 py-1 rounded border border-gray-700 transition-colors"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>
              <pre className="p-3 rounded-lg bg-black/60 border border-gray-800 font-mono text-xs text-emerald-300 overflow-x-auto">
                <code>{finding.suggested_code}</code>
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FindingCard;
