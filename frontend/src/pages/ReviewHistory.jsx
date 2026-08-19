import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  History, 
  FileCode, 
  Trash2, 
  Search, 
  ExternalLink, 
  PlusCircle, 
  Sparkles,
  AlertCircle
} from 'lucide-react';
import { reviewsAPI } from '../services/api';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';

const ReviewHistory = () => {
  const [reviews, setReviews] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      const res = await reviewsAPI.getUserReviews(100, 0);
      setReviews(res.data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm('Delete this code review?')) return;
    try {
      await reviewsAPI.deleteReview(id);
      setReviews(reviews.filter((r) => r.id !== id));
    } catch (err) {
      setError(err);
    }
  };

  const filteredReviews = reviews.filter((r) =>
    r.filename.toLowerCase().includes(search.toLowerCase()) ||
    r.source_type.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return <Loading message="Loading review history..." />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <History className="w-6 h-6 text-indigo-400" /> Review History
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Browse, inspect, and manage all your historical AI and static code analyses.
          </p>
        </div>

        <Link
          to="/review/new"
          className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2 self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" /> New Review
        </Link>
      </div>

      <ErrorMessage error={error} onDismiss={() => setError(null)} />

      {/* Search Bar */}
      <div className="relative">
        <Search className="w-5 h-5 text-gray-500 absolute left-4 top-3.5" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter reviews by filename or source type..."
          className="w-full pl-12 pr-4 py-3 bg-[#111827] border border-gray-800 rounded-2xl text-sm text-white placeholder-gray-500 focus:border-indigo-500 outline-none transition-all"
        />
      </div>

      {/* Reviews List */}
      {filteredReviews.length > 0 ? (
        <div className="bg-[#111827] border border-gray-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-xs font-semibold text-gray-400 uppercase tracking-wider bg-gray-900/50">
                  <th className="py-4 px-6">Filename</th>
                  <th className="py-4 px-4">Source</th>
                  <th className="py-4 px-4">Score</th>
                  <th className="py-4 px-4">Findings</th>
                  <th className="py-4 px-4">Date</th>
                  <th className="py-4 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {filteredReviews.map((r) => (
                  <tr key={r.id} className="hover:bg-gray-800/40 transition-colors">
                    <td className="py-4 px-6 font-mono text-sm font-semibold text-white">
                      <Link to={`/review/${r.id}`} className="hover:text-indigo-400 transition-colors flex items-center gap-2">
                        <FileCode className="w-4 h-4 text-indigo-400 flex-shrink-0" />
                        {r.filename}
                      </Link>
                    </td>
                    <td className="py-4 px-4">
                      <span className="text-xs px-2.5 py-1 rounded-full bg-gray-800 text-gray-300 border border-gray-700">
                        {r.source_type}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`text-xs px-2.5 py-1 rounded-full font-bold border ${
                        r.overall_score >= 80
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : r.overall_score >= 60
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                            : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                      }`}>
                        {r.overall_score} / 100
                      </span>
                    </td>
                    <td className="py-4 px-4 text-gray-300 font-medium">
                      {r.findings_count} issue(s)
                    </td>
                    <td className="py-4 px-4 text-xs text-gray-400">
                      {new Date(r.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-4 px-6 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={`/review/${r.id}`}
                          className="p-1.5 rounded-lg bg-gray-800 hover:bg-indigo-600 text-gray-300 hover:text-white transition-colors"
                          title="Open Details"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </Link>
                        <button
                          onClick={(e) => handleDelete(r.id, e)}
                          className="p-1.5 rounded-lg bg-gray-800 hover:bg-rose-950/60 text-gray-400 hover:text-rose-400 transition-colors"
                          title="Delete Review"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="p-12 text-center bg-[#111827] rounded-3xl border border-gray-800">
          <History className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-white">No reviews found</h3>
          <p className="text-xs text-gray-400 mt-1 mb-4">
            {search ? 'Try adjusting your search query.' : 'Submit a Python snippet or repository to get started.'}
          </p>
          <Link
            to="/review/new"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500 transition-colors"
          >
            <PlusCircle className="w-4 h-4" /> Start Review
          </Link>
        </div>
      )}
    </div>
  );
};

export default ReviewHistory;
