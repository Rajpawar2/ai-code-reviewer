import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  FileCode, 
  Trash2, 
  ArrowLeft, 
  Sparkles, 
  Shield, 
  Zap, 
  Wrench, 
  Bug, 
  Code, 
  CheckCircle2, 
  AlertTriangle,
  Copy,
  Check,
  Cpu
} from 'lucide-react';
import { reviewsAPI } from '../services/api';
import ScoreCard from '../components/ScoreCard';
import FindingCard from '../components/FindingCard';
import CodeEditor from '../components/CodeEditor';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';

const ReviewDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchReview();
  }, [id]);

  const fetchReview = async () => {
    try {
      setLoading(true);
      const res = await reviewsAPI.getReviewById(id);
      setReview(res.data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this review?')) return;
    setDeleting(true);
    try {
      await reviewsAPI.deleteReview(id);
      navigate('/reviews');
    } catch (err) {
      setError(err);
      setDeleting(false);
    }
  };

  if (loading) {
    return <Loading message="Retrieving code review metrics and findings..." />;
  }

  if (!review) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <ErrorMessage error="Review not found or has been deleted." />
        <Link to="/dashboard" className="text-indigo-400 text-sm font-semibold hover:underline">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  const findings = review.findings || [];
  const bugFindings = findings.filter(f => f.category === 'bug' || f.category === 'ast');
  const securityFindings = findings.filter(f => f.category === 'security');
  const performanceFindings = findings.filter(f => f.category === 'performance');
  const qualityFindings = findings.filter(f => f.category === 'quality' || f.category === 'lint' || f.category === 'complexity' || f.category === 'maintainability');

  const tabs = [
    { id: 'overview', label: 'Overview', count: findings.length },
    { id: 'bugs', label: 'Bugs', count: bugFindings.length, icon: Bug },
    { id: 'security', label: 'Security', count: securityFindings.length, icon: Shield },
    { id: 'performance', label: 'Performance', count: performanceFindings.length, icon: Zap },
    { id: 'quality', label: 'Code Quality', count: qualityFindings.length, icon: Sparkles },
    { id: 'fixed_code', label: 'Fixed Code', count: null, icon: Code },
    { id: 'source', label: 'Source Code', count: null, icon: FileCode },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Navigation & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            to="/reviews"
            className="p-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-white tracking-tight">{review.filename}</h1>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono">
                {review.source_type}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-0.5">
              Analyzed on {new Date(review.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        <button
          onClick={handleDelete}
          disabled={deleting}
          className="px-4 py-2 rounded-xl bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-800/40 text-xs font-semibold transition-colors flex items-center gap-2 self-start sm:self-auto"
        >
          <Trash2 className="w-4 h-4" />
          {deleting ? 'Deleting...' : 'Delete Review'}
        </button>
      </div>

      <ErrorMessage error={error} onDismiss={() => setError(null)} />

      {/* Score Summary Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <ScoreCard title="Overall Score" score={review.overall_score} type="default" />
        <ScoreCard title="Security" score={review.security_score} type="security" />
        <ScoreCard title="Quality" score={review.quality_score} type="quality" />
        <ScoreCard title="Performance" score={review.performance_score} type="performance" />
        <ScoreCard title="Maintainability" score={review.maintainability_score} type="maintainability" />
      </div>

      {/* AI Review Summary Box */}
      {review.ai_summary && (
        <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-950/40 via-purple-950/20 to-gray-900 border border-indigo-500/30 shadow-xl space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 uppercase tracking-wider">
            <Cpu className="w-4 h-4" /> AI Assistant Synthesis
          </div>
          <p className="text-sm text-gray-200 leading-relaxed">{review.ai_summary}</p>
        </div>
      )}

      {/* Main Tabs Navigation */}
      <div className="border-b border-gray-800 flex items-center gap-2 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-3 text-sm font-semibold border-b-2 transition-all flex items-center gap-2 whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
                : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-700'
            }`}
          >
            {tab.icon && <tab.icon className="w-4 h-4" />}
            {tab.label}
            {tab.count !== null && (
              <span className={`text-xs px-2 py-0.5 rounded-full ${
                activeTab === tab.id ? 'bg-indigo-500/20 text-indigo-300' : 'bg-gray-800 text-gray-400'
              }`}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Contents */}
      <div className="space-y-4">
        {activeTab === 'overview' && (
          <div className="space-y-4">
            {findings.length > 0 ? (
              findings.map((f) => <FindingCard key={f.id} finding={f} />)
            ) : (
              <div className="p-8 text-center bg-emerald-950/20 border border-emerald-800/40 rounded-2xl">
                <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
                <h4 className="text-base font-bold text-emerald-300">Clean Code! No issues detected.</h4>
                <p className="text-xs text-emerald-400/80 mt-1">Code passes AST, Ruff, Bandit, and Radon checks seamlessly.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'bugs' && (
          <div className="space-y-4">
            {bugFindings.length > 0 ? (
              bugFindings.map((f) => <FindingCard key={f.id} finding={f} />)
            ) : (
              <p className="text-gray-400 text-sm text-center py-8">No functional bugs detected.</p>
            )}
          </div>
        )}

        {activeTab === 'security' && (
          <div className="space-y-4">
            {securityFindings.length > 0 ? (
              securityFindings.map((f) => <FindingCard key={f.id} finding={f} />)
            ) : (
              <p className="text-gray-400 text-sm text-center py-8">No security vulnerabilities detected.</p>
            )}
          </div>
        )}

        {activeTab === 'performance' && (
          <div className="space-y-4">
            {performanceFindings.length > 0 ? (
              performanceFindings.map((f) => <FindingCard key={f.id} finding={f} />)
            ) : (
              <p className="text-gray-400 text-sm text-center py-8">No performance bottlenecks detected.</p>
            )}
          </div>
        )}

        {activeTab === 'quality' && (
          <div className="space-y-4">
            {qualityFindings.length > 0 ? (
              qualityFindings.map((f) => <FindingCard key={f.id} finding={f} />)
            ) : (
              <p className="text-gray-400 text-sm text-center py-8">Code quality and styling adhere to standards.</p>
            )}
          </div>
        )}

        {activeTab === 'fixed_code' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">
                AI-refactored, secured, and optimized code generated by Qwen2.5-Coder.
              </span>
            </div>
            {review.fixed_code ? (
              <CodeEditor
                value={review.fixed_code}
                readOnly={true}
                language="python"
                height="500px"
                title="AI Corrected & Refactored Code"
                showCopy={true}
              />
            ) : (
              <div className="p-8 text-center bg-gray-900/40 rounded-2xl border border-gray-800">
                <p className="text-sm text-gray-400">No fixed code generated for this review.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'source' && (
          <div className="space-y-3">
            <CodeEditor
              value={review.source_code}
              readOnly={true}
              language="python"
              height="500px"
              title={`Original Source: ${review.filename}`}
              showCopy={true}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewDetails;
