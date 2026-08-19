import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { User, Mail, Calendar, Shield, Cpu, Key, Database } from 'lucide-react';
import { healthAPI } from '../services/api';

const Profile = () => {
  const { user } = useAuth();
  const [ollamaInfo, setOllamaInfo] = useState(null);

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const res = await healthAPI.getOllamaHealth();
        setOllamaInfo(res.data);
      } catch (err) {
        setOllamaInfo({ available: false });
      }
    };
    fetchInfo();
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">User Profile & Environment</h1>
        <p className="text-sm text-gray-400 mt-1">Manage your account information and view local engine configuration.</p>
      </div>

      <div className="bg-[#111827] border border-gray-800 rounded-3xl p-6 sm:p-8 shadow-xl space-y-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-xl font-bold text-white shadow-lg shadow-indigo-600/30">
            {user?.name ? user.name[0].toUpperCase() : 'U'}
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">{user?.name}</h2>
            <p className="text-sm text-gray-400 font-mono">{user?.email}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-gray-800">
          <div className="p-4 rounded-2xl bg-gray-900/60 border border-gray-800 flex items-center gap-3">
            <User className="w-5 h-5 text-indigo-400" />
            <div>
              <span className="text-xs text-gray-500 uppercase tracking-wider block">Full Name</span>
              <span className="text-sm font-semibold text-white">{user?.name}</span>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-gray-900/60 border border-gray-800 flex items-center gap-3">
            <Mail className="w-5 h-5 text-indigo-400" />
            <div>
              <span className="text-xs text-gray-500 uppercase tracking-wider block">Email Address</span>
              <span className="text-sm font-semibold text-white">{user?.email}</span>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-gray-900/60 border border-gray-800 flex items-center gap-3">
            <Calendar className="w-5 h-5 text-indigo-400" />
            <div>
              <span className="text-xs text-gray-500 uppercase tracking-wider block">Member Since</span>
              <span className="text-sm font-semibold text-white">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Active'}
              </span>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-gray-900/60 border border-gray-800 flex items-center gap-3">
            <Shield className="w-5 h-5 text-indigo-400" />
            <div>
              <span className="text-xs text-gray-500 uppercase tracking-wider block">Auth Level</span>
              <span className="text-sm font-semibold text-emerald-400">JWT Authenticated</span>
            </div>
          </div>
        </div>
      </div>

      {/* System Diagnostics Card */}
      <div className="bg-[#111827] border border-gray-800 rounded-3xl p-6 sm:p-8 shadow-xl space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-400" /> AI & Engine Diagnostics
        </h3>
        
        <div className="space-y-3 text-sm">
          <div className="flex items-center justify-between p-3 rounded-xl bg-gray-900 border border-gray-800">
            <span className="text-gray-400">Ollama LLM Provider:</span>
            <span className="font-mono font-semibold text-indigo-300">
              {ollamaInfo?.available ? 'Connected' : 'Offline / Fallback'}
            </span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-xl bg-gray-900 border border-gray-800">
            <span className="text-gray-400">Target Model:</span>
            <span className="font-mono text-gray-200">qwen2.5-coder:7b</span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-xl bg-gray-900 border border-gray-800">
            <span className="text-gray-400">Deterministic Analyzers:</span>
            <span className="font-semibold text-emerald-400">Python AST, Ruff, Bandit, Radon</span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-xl bg-gray-900 border border-gray-800">
            <span className="text-gray-400">Database Engine:</span>
            <span className="font-mono text-gray-200">PostgreSQL (SQLAlchemy 2.0)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
