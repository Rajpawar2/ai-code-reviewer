import React from 'react';
import { Shield, Sparkles, Zap, Wrench, Award } from 'lucide-react';

const ScoreCard = ({ title, score, type = 'default', subtitle }) => {
  const getScoreColor = (val) => {
    if (val >= 85) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    if (val >= 70) return 'text-blue-400 border-blue-500/30 bg-blue-500/10';
    if (val >= 50) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
  };

  const getProgressColor = (val) => {
    if (val >= 85) return 'bg-emerald-500';
    if (val >= 70) return 'bg-blue-500';
    if (val >= 50) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  const getIcon = () => {
    switch (type) {
      case 'security':
        return <Shield className="w-5 h-5 text-indigo-400" />;
      case 'quality':
        return <Sparkles className="w-5 h-5 text-violet-400" />;
      case 'performance':
        return <Zap className="w-5 h-5 text-amber-400" />;
      case 'maintainability':
        return <Wrench className="w-5 h-5 text-teal-400" />;
      default:
        return <Award className="w-5 h-5 text-indigo-400" />;
    }
  };

  return (
    <div className="bg-[#111827] border border-gray-800/80 rounded-2xl p-5 shadow-xl relative overflow-hidden group hover:border-gray-700 transition-all">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">{title}</span>
        <div className="p-2 rounded-xl bg-gray-800/80 border border-gray-700/50">
          {getIcon()}
        </div>
      </div>

      <div className="flex items-baseline gap-2 mb-3">
        <span className="text-3xl font-extrabold text-white tracking-tight">{score}</span>
        <span className="text-xs font-semibold text-gray-500">/ 100</span>
      </div>

      <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden mb-2">
        <div 
          className={`h-full rounded-full transition-all duration-1000 ${getProgressColor(score)}`}
          style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
        ></div>
      </div>

      {subtitle && (
        <p className="text-xs text-gray-400">{subtitle}</p>
      )}
    </div>
  );
};

export default ScoreCard;
