import React, { useState } from 'react';
import { 
  Github, 
  Search, 
  FileCode, 
  ShieldAlert, 
  AlertTriangle, 
  CheckCircle2, 
  Sparkles, 
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Layers
} from 'lucide-react';
import { githubAPI } from '../services/api';
import ScoreCard from '../components/ScoreCard';
import FindingCard from '../components/FindingCard';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';

const GithubAnalysis = () => {
  const [repoUrl, setRepoUrl] = useState('https://github.com/pallets/click');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [expandedFile, setExpandedFile] = useState(null);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!repoUrl.trim()) {
      setError('Please provide a valid GitHub repository URL.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await githubAPI.analyzeRepo({ repository_url: repoUrl.trim() });
      setResult(res.data);
      if (res.data.top_problematic_files?.length > 0) {
        setExpandedFile(res.data.top_problematic_files[0].filename);
      }
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <Github className="w-7 h-7 text-indigo-400" /> GitHub Repository Analysis
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Perform holistic static code review and AI vulnerability scanning across all Python files in a GitHub repo.
        </p>
      </div>

      <ErrorMessage error={error} onDismiss={() => setError(null)} />

      {/* Repo Input Box */}
      <form onSubmit={handleAnalyze} className="bg-[#111827] border border-gray-800 rounded-3xl p-6 shadow-xl space-y-4">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-gray-300 mb-2">
            GitHub Repository HTTPS URL
          </label>
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Github className="w-5 h-5 text-gray-500 absolute left-4 top-3.5" />
              <input
                type="url"
                required
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/psf/requests"
                className="w-full pl-12 pr-4 py-3 bg-gray-900 border border-gray-800 rounded-2xl text-sm text-white placeholder-gray-500 focus:border-indigo-500 outline-none transition-all font-mono"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-sm rounded-2xl shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center gap-2 flex-shrink-0"
            >
              <Search className="w-4 h-4" />
              {loading ? 'Scanning...' : 'Analyze Repository'}
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-gray-400 pt-1">
          <span className="font-semibold text-gray-500">Popular Examples:</span>
          <button
            type="button"
            onClick={() => setRepoUrl('https://github.com/psf/requests')}
            className="hover:text-indigo-400 underline underline-offset-2"
          >
            psf/requests
          </button>
          <span>•</span>
          <button
            type="button"
            onClick={() => setRepoUrl('https://github.com/pallets/click')}
            className="hover:text-indigo-400 underline underline-offset-2"
          >
            pallets/click
          </button>
          <span>•</span>
          <button
            type="button"
            onClick={() => setRepoUrl('https://github.com/encode/uvicorn')}
            className="hover:text-indigo-400 underline underline-offset-2"
          >
            encode/uvicorn
          </button>
        </div>
      </form>

      {loading && (
        <div className="bg-[#111827] border border-gray-800 rounded-3xl p-12 shadow-2xl text-center">
          <Loading message="Cloning repo, extracting Python files, executing AST, Ruff, Bandit, Radon & AI review..." />
          <p className="text-xs text-gray-500 mt-2">
            This may take 10-30 seconds depending on repository size.
          </p>
        </div>
      )}

      {/* Results Section */}
      {result && !loading && (
        <div className="space-y-8 animate-fade-in">
          {/* Top Repository Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <ScoreCard 
              title="Repository Score" 
              score={result.repository_score} 
              type="default" 
              subtitle={`Analyzed ${result.total_files_analyzed} Python files`}
            />
            <ScoreCard 
              title="Total Findings" 
              score={Math.max(0, 100 - (result.total_findings * 3))} 
              type="quality"
              subtitle={`${result.total_findings} total issue(s) identified`}
            />
            <ScoreCard 
              title="Critical Issues" 
              score={Math.max(0, 100 - (result.critical_issues_count * 20))} 
              type="security"
              subtitle={`${result.critical_issues_count} critical severities`}
            />
            <div className="bg-[#111827] border border-gray-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">Avg Complexity</span>
              <div className="my-2">
                <span className={`text-2xl font-extrabold px-3 py-1 rounded-xl border ${
                  result.average_complexity === 'LOW'
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                    : result.average_complexity === 'MEDIUM'
                      ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                }`}>
                  {result.average_complexity}
                </span>
              </div>
              <p className="text-xs text-gray-400">Radon cyclomatic rank</p>
            </div>
          </div>

          {/* Top Problematic Files */}
          {result.top_problematic_files?.length > 0 && (
            <div className="bg-[#111827] border border-gray-800 rounded-3xl p-6 shadow-xl space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-rose-400" /> Top Problematic Files
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {result.top_problematic_files.map((file, idx) => (
                  <div 
                    key={idx}
                    onClick={() => setExpandedFile(expandedFile === file.filename ? null : file.filename)}
                    className="p-4 rounded-2xl bg-gray-900/60 border border-gray-800 hover:border-gray-700 cursor-pointer transition-all space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-semibold text-white truncate max-w-[200px]" title={file.filename}>
                        {file.filename}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-bold border ${
                        file.overall_score >= 80
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                      }`}>
                        {file.overall_score}/100
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-400">
                      <span>{file.lines_of_code} LOC</span>
                      <span>•</span>
                      <span>{file.findings.length} issue(s)</span>
                      <span>•</span>
                      <span className="font-mono">CC: {file.complexity}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* File-by-file breakdown */}
          <div className="bg-[#111827] border border-gray-800 rounded-3xl p-6 shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" /> All Analyzed Files ({result.all_files?.length})
            </h3>

            <div className="space-y-3">
              {result.all_files?.map((file, idx) => {
                const isExpanded = expandedFile === file.filename;
                return (
                  <div key={idx} className="border border-gray-800 rounded-2xl overflow-hidden bg-gray-900/40">
                    <div 
                      onClick={() => setExpandedFile(isExpanded ? null : file.filename)}
                      className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-800/40 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <FileCode className="w-4 h-4 text-indigo-400" />
                        <span className="font-mono text-sm font-semibold text-white">{file.filename}</span>
                        <span className="text-xs px-2 py-0.5 rounded-md bg-gray-800 text-gray-400">
                          {file.lines_of_code} LOC
                        </span>
                      </div>

                      <div className="flex items-center gap-4">
                        <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold border ${
                          file.overall_score >= 80
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                        }`}>
                          Score: {file.overall_score}
                        </span>
                        <span className="text-xs text-gray-400">
                          {file.findings.length} findings
                        </span>
                        {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="p-4 border-t border-gray-800 space-y-3 bg-[#0D121F]">
                        {file.findings.length > 0 ? (
                          file.findings.map((f, fIdx) => (
                            <FindingCard key={fIdx} finding={f} />
                          ))
                        ) : (
                          <p className="text-xs text-emerald-400 py-2 flex items-center gap-1.5">
                            <CheckCircle2 className="w-4 h-4" /> No issues detected in this file.
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GithubAnalysis;
