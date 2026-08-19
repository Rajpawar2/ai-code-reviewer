import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Code2, 
  LogOut, 
  User as UserIcon, 
  Cpu,
  Github,
  History,
  LayoutDashboard,
  PlusCircle,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { healthAPI } from '../services/api';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [ollamaStatus, setOllamaStatus] = useState({ available: false, loading: true });

  useEffect(() => {
    const checkOllama = async () => {
      try {
        const res = await healthAPI.getOllamaHealth();
        setOllamaStatus({ available: res.data.available, model: res.data.model, loading: false });
      } catch (err) {
        setOllamaStatus({ available: false, loading: false });
      }
    };
    checkOllama();
    const interval = setInterval(checkOllama, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-gray-800 bg-[#0B0F19]/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              <Code2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-lg text-white tracking-tight flex items-center gap-1.5">
                RevAI <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-medium">Assistant</span>
              </span>
            </div>
          </Link>

          {isAuthenticated && (
            <nav className="hidden md:flex items-center gap-1">
              <Link 
                to="/dashboard" 
                className="px-3.5 py-2 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-800/60 transition-colors flex items-center gap-2"
              >
                <LayoutDashboard className="w-4 h-4 text-gray-400" />
                Dashboard
              </Link>
              <Link 
                to="/review/new" 
                className="px-3.5 py-2 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-800/60 transition-colors flex items-center gap-2"
              >
                <PlusCircle className="w-4 h-4 text-indigo-400" />
                New Review
              </Link>
              <Link 
                to="/reviews" 
                className="px-3.5 py-2 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-800/60 transition-colors flex items-center gap-2"
              >
                <History className="w-4 h-4 text-gray-400" />
                History
              </Link>
              <Link 
                to="/github" 
                className="px-3.5 py-2 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-800/60 transition-colors flex items-center gap-2"
              >
                <Github className="w-4 h-4 text-gray-400" />
                GitHub Analysis
              </Link>
            </nav>
          )}
        </div>

        <div className="flex items-center gap-3">
          {/* Ollama Status Pill */}
          <div className={`hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border ${
            ollamaStatus.available 
              ? 'bg-emerald-950/40 text-emerald-300 border-emerald-800/60' 
              : 'bg-amber-950/40 text-amber-300 border-amber-800/60'
          }`}>
            <Cpu className="w-3.5 h-3.5" />
            <span>Ollama: {ollamaStatus.available ? 'Connected' : 'Offline'}</span>
            <span className={`w-2 h-2 rounded-full ${ollamaStatus.available ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`}></span>
          </div>

          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <Link
                to="/profile"
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm text-gray-300 hover:text-white hover:bg-gray-800 transition-colors"
              >
                <div className="w-7 h-7 rounded-full bg-indigo-600/30 border border-indigo-500/30 flex items-center justify-center text-xs font-bold text-indigo-300">
                  {user?.name ? user.name[0].toUpperCase() : 'U'}
                </div>
                <span className="hidden lg:inline text-xs font-medium">{user?.name}</span>
              </Link>
              <button
                onClick={handleLogout}
                title="Logout"
                className="p-2 rounded-lg text-gray-400 hover:text-red-400 hover:bg-red-950/30 border border-transparent hover:border-red-800/40 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="px-4 py-2 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-800 transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 rounded-lg text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20 transition-colors"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
