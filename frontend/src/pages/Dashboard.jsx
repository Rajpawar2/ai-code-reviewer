import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  FileCode, 
  ShieldAlert, 
  Sparkles, 
  ArrowUpRight, 
  PlusCircle, 
  History, 
  Github, 
  CheckCircle2, 
  AlertTriangle,
  Award,
  Zap,
  Wrench
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip 
} from 'recharts';
import { reviewsAPI } from '../services/api';
import ScoreCard from '../components/ScoreCard';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      const res = await reviewsAPI.getDashboardStats();
      setStats(res.data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loading message="Loading workspace metrics & recent reviews..." />;
  }

  const radarData = stats ? [
    { subject: 'Security', value: stats.security_avg, fullMark: 100 },
    { subject: 'Quality', value: stats.quality_avg, fullMark: 100 },
    { subject: 'Performance', value: stats.performance_avg, fullMark: 100 },
    { subject: 'Maintainability', value: stats.maintainability_avg, fullMark: 100 },
    { subject: 'Overall', value: stats.average_score, fullMark: 100 },
  ] : [];

  const recentBarData = stats?.recent_reviews?.slice(0, 6).map((r, idx) => ({
    name: r.filename.length > 12 ? r.filename.substring(0, 10) + '..' : r.filename,
    score: r.overall_score,
  })) || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-indigo-900/30 via-purple-900/20 to-gray-900 border border-indigo-500/20 rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
        <div className="space-y-2 z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" /> AI Engine Active (Ollama Qwen2.5-Coder)
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Code Health Dashboard</h1>
          <p className="text-sm text-gray-400 max-w-xl">
            Real-time static code analysis & AI debugging metrics across your Python scripts and repositories.
          </p>
        </div>

        <div className="flex items-center gap-3 z-10">
          <Link
            to="/review/new"
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2"
          >
            <PlusCircle className="w-4 h-4" /> Start Review
          </Link>
          <Link
            to="/github"
            className="px-4 py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-200 font-medium text-sm border border-gray-700 transition-all flex items-center gap-2"
          >
            <Github className="w-4 h-4" /> Analyze Repo
          </Link>
        </div>
      </div>

      <ErrorMessage error={error} onDismiss={() => setError(null)} />

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <ScoreCard 
          title="Average Health Score" 
          score={stats?.average_score || 100} 
          type="default"
          subtitle={`Calculated across ${stats?.total_reviews || 0} reviews`}
        />
        <ScoreCard 
          title="Security Score" 
          score={stats?.security_avg || 100} 
          type="security"
          subtitle={`${stats?.security_issues_count || 0} security issues detected`}
        />
        <ScoreCard 
          title="Code Quality" 
          score={stats?.quality_avg || 100} 
          type="quality"
          subtitle="AST and Ruff rule compliance"
        />
        <ScoreCard 
          title="Maintainability" 
          score={stats?.maintainability_avg || 100} 
          type="maintainability"
          subtitle="Radon cyclomatic complexity index"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Radar Chart */}
        <div className="lg:col-span-6 bg-[#111827] border border-gray-800 rounded-3xl p-6 shadow-xl flex flex-col">
          <h3 className="text-base font-bold text-white mb-2">Multi-Dimensional Quality Analysis</h3>
          <p className="text-xs text-gray-400 mb-4">Holistic score profile across all analysis facets</p>
          <div className="h-64 w-full flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid stroke="#374151" />
                <PolarAngleAxis dataKey="subject" stroke="#9CA3AF" tick={{ fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#4B5563" />
                <Radar name="Score" dataKey="value" stroke="#6366F1" fill="#6366F1" fillOpacity={0.4} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Scores Bar Chart */}
        <div className="lg:col-span-6 bg-[#111827] border border-gray-800 rounded-3xl p-6 shadow-xl flex flex-col">
          <h3 className="text-base font-bold text-white mb-2">Recent Review Scores</h3>
          <p className="text-xs text-gray-400 mb-4">Overall scores of your most recent code submissions</p>
          <div className="h-64 w-full flex-1">
            {recentBarData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={recentBarData}>
                  <XAxis dataKey="name" stroke="#9CA3AF" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} stroke="#9CA3AF" tick={{ fontSize: 11 }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', borderRadius: '0.75rem', color: '#fff' }}
                  />
                  <Bar dataKey="score" fill="#818CF8" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500 text-sm">
                No recent review data to display.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Reviews Table */}
      <div className="bg-[#111827] border border-gray-800 rounded-3xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-bold text-white">Recent Reviews</h3>
            <p className="text-xs text-gray-400 mt-0.5">Quickly access or inspect previous code analysis results</p>
          </div>
          <Link
            to="/reviews"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            View all history <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {stats?.recent_reviews && stats.recent_reviews.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  <th className="pb-3">File / Script</th>
                  <th className="pb-3">Source Type</th>
                  <th className="pb-3">Health Score</th>
                  <th className="pb-3">Issues Found</th>
                  <th className="pb-3">AI Engine</th>
                  <th className="pb-3">Date</th>
                  <th className="pb-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {stats.recent_reviews.map((rev) => (
                  <tr key={rev.id} className="hover:bg-gray-800/30 transition-colors">
                    <td className="py-3.5 font-mono text-sm font-medium text-white flex items-center gap-2">
                      <FileCode className="w-4 h-4 text-indigo-400" />
                      {rev.filename}
                    </td>
                    <td className="py-3.5">
                      <span className="text-xs px-2.5 py-1 rounded-full bg-gray-800 text-gray-300 border border-gray-700">
                        {rev.source_type}
                      </span>
                    </td>
                    <td className="py-3.5">
                      <span className={`text-xs px-2.5 py-1 rounded-full font-bold border ${
                        rev.overall_score >= 80 
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : rev.overall_score >= 60 
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                            : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                      }`}>
                        {rev.overall_score} / 100
                      </span>
                    </td>
                    <td className="py-3.5 text-gray-300 font-medium">
                      {rev.findings_count} issue(s)
                    </td>
                    <td className="py-3.5">
                      <span className="text-xs text-indigo-300 font-medium">
                        {rev.ai_available ? 'Qwen2.5-Coder' : 'Static Fallback'}
                      </span>
                    </td>
                    <td className="py-3.5 text-xs text-gray-400">
                      {new Date(rev.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3.5 text-right">
                      <Link
                        to={`/review/${rev.id}`}
                        className="text-xs px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-indigo-600 text-gray-300 hover:text-white border border-gray-700 hover:border-indigo-500 transition-all inline-flex items-center gap-1"
                      >
                        Inspect
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center bg-gray-900/40 rounded-2xl border border-gray-800/80">
            <FileCode className="w-10 h-10 text-gray-600 mx-auto mb-3" />
            <p className="text-sm font-medium text-gray-300">No code reviews created yet</p>
            <p className="text-xs text-gray-500 mt-1 mb-4">Paste code or upload a Python script to start your first review.</p>
            <Link
              to="/review/new"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500 transition-colors"
            >
              <PlusCircle className="w-4 h-4" /> Start Review Now
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
