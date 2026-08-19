import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Play, 
  RotateCcw, 
  Upload, 
  FileCode, 
  Sparkles, 
  Check, 
  Cpu, 
  FileText,
  AlertCircle
} from 'lucide-react';
import { reviewsAPI } from '../services/api';
import CodeEditor from '../components/CodeEditor';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';

const SAMPLES = {
  buggy: `# Sample 1: Buggy Python Code
def append_to_list(val, my_list=[]):
    """Bug: Mutable default argument accumulates state across calls."""
    my_list.append(val)
    return my_list

def divide_numbers(a, b):
    """Bug: Bare except hides ZeroDivisionError and typing issues."""
    try:
        res = a / b
        return res
    except:
        pass

def calculate_discount(price, discount=None):
    """Bug: '== None' comparison and unreachable code."""
    if discount == None:
        discount = 0.0
        return price
        # Dead code
        extra_discount = 5.0
        price -= extra_discount

    return price * (1 - discount)
`,
  insecure: `# Sample 2: Insecure Python Code (Vulnerabilities)
import subprocess
import hashlib
import random

SECRET_API_KEY = "sk-live-98742398471239847192837419283"
DATABASE_PASSWORD = "SuperSecretPassword123!"

def execute_user_script(user_script_input):
    """Vulnerability: Arbitrary code execution via eval/exec."""
    exec(user_script_input)
    return eval(f"1 + {user_script_input}")

def run_system_ping(host):
    """Vulnerability: Command Injection via shell=True."""
    command = f"ping -c 1 {host}"
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()

def generate_reset_token():
    """Vulnerability: Insecure pseudo-random number generator for tokens & MD5."""
    token = str(random.randint(100000, 999999))
    return hashlib.md5(token.encode()).hexdigest()
`,
  complex: `# Sample 3: High Complexity Python Code
def complex_decision_matrix(a, b, c, d, mode, flag, items):
    result = 0
    if mode == "A":
        if flag:
            for item in items:
                for sub_item in item.get("sub_items", []):
                    for leaf in sub_item.get("leaves", []):
                        if leaf.get("val") > 10:
                            if a > b and c < d:
                                result += leaf.get("val") * 2
                            elif a == b:
                                result += leaf.get("val") + 1
                            else:
                                result -= 1
                        else:
                            if mode != "B" and flag:
                                result += 5
    elif mode == "B":
        while a > 0:
            while b > 0:
                while c > 0:
                    c -= 1
                    result += 1
                b -= 1
            a -= 1
    return result
`,
  clean: `# Sample 4: Clean & Idiomatic Python
from typing import List, Optional, Dict, Any

class UserRecordManager:
    """Clean, well-structured Python class following PEP 8 conventions."""

    def __init__(self, initial_records: Optional[List[Dict[str, Any]]] = None) -> None:
        self.records: List[Dict[str, Any]] = initial_records if initial_records is not None else []

    def add_user(self, user_id: str, email: str, role: str = "member") -> Dict[str, Any]:
        record = {
            "id": user_id,
            "email": email.strip().lower(),
            "role": role,
            "is_active": True
        }
        self.records.append(record)
        return record

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        target_email = email.strip().lower()
        for user in self.records:
            if user.get("email") == target_email:
                return user
        return None
`
};

const NewReview = () => {
  const [code, setCode] = useState(SAMPLES.buggy);
  const [filename, setFilename] = useState('buggy_script.py');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSampleClick = (key) => {
    setCode(SAMPLES[key]);
    setFilename(`${key}_example.py`);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.py')) {
      setError('Please upload a Python (.py) file.');
      return;
    }

    setFilename(file.name);
    const reader = new FileReader();
    reader.onload = (event) => {
      setCode(event.target.result);
      setError(null);
    };
    reader.readAsText(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!code.trim()) {
      setError('Please provide Python source code to analyze.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await reviewsAPI.createSnippetReview({
        filename: filename.trim() || 'code_snippet.py',
        source_code: code,
        source_type: 'snippet'
      });
      navigate(`/review/${res.data.id}`);
    } catch (err) {
      setError(err);
      setLoading(false);
    }
  };

  const handleClear = () => {
    setCode('');
    setFilename('snippet.py');
    setError(null);
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20">
        <div className="bg-[#111827] border border-gray-800 rounded-3xl p-12 shadow-2xl text-center">
          <Loading message="Executing AST, Ruff, Bandit, Radon & Ollama Qwen2.5-Coder AI Review..." />
          <p className="text-xs text-gray-500 mt-4">
            Performing multi-pass deterministic scanning and generating structured recommendations.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-indigo-400" /> New Code Review
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Submit Python source code for AST parsing, security linting, complexity checks, and AI debugging.
          </p>
        </div>

        {/* Quick Sample Presets */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Presets:</span>
          <button
            type="button"
            onClick={() => handleSampleClick('buggy')}
            className="px-2.5 py-1 rounded-lg bg-rose-950/40 text-rose-300 border border-rose-800/40 text-xs font-medium hover:bg-rose-900/60 transition-colors"
          >
            Buggy
          </button>
          <button
            type="button"
            onClick={() => handleSampleClick('insecure')}
            className="px-2.5 py-1 rounded-lg bg-red-950/40 text-red-300 border border-red-800/40 text-xs font-medium hover:bg-red-900/60 transition-colors"
          >
            Insecure
          </button>
          <button
            type="button"
            onClick={() => handleSampleClick('complex')}
            className="px-2.5 py-1 rounded-lg bg-purple-950/40 text-purple-300 border border-purple-800/40 text-xs font-medium hover:bg-purple-900/60 transition-colors"
          >
            Complex
          </button>
          <button
            type="button"
            onClick={() => handleSampleClick('clean')}
            className="px-2.5 py-1 rounded-lg bg-emerald-950/40 text-emerald-300 border border-emerald-800/40 text-xs font-medium hover:bg-emerald-900/60 transition-colors"
          >
            Clean
          </button>
        </div>
      </div>

      <ErrorMessage error={error} onDismiss={() => setError(null)} />

      {/* Editor & Submission Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-[#111827] border border-gray-800 p-4 rounded-2xl">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <FileCode className="w-5 h-5 text-indigo-400 flex-shrink-0" />
            <input
              type="text"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              placeholder="filename.py"
              className="bg-gray-900 border border-gray-800 rounded-xl px-3 py-1.5 text-sm text-white font-mono focus:border-indigo-500 outline-none w-full sm:w-64"
            />
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
            <label className="cursor-pointer px-3.5 py-1.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs font-medium border border-gray-700 transition-colors flex items-center gap-1.5">
              <Upload className="w-3.5 h-3.5" />
              Upload .py file
              <input
                type="file"
                accept=".py"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
            <button
              type="button"
              onClick={handleClear}
              className="px-3.5 py-1.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-medium border border-gray-700 transition-colors flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Clear
            </button>
          </div>
        </div>

        {/* Monaco Editor Container */}
        <CodeEditor
          value={code}
          onChange={(val) => setCode(val || '')}
          language="python"
          height="460px"
          title={`Editing: ${filename}`}
          showCopy={true}
        />

        {/* Action Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading || !code.trim()}
            className="px-8 py-3.5 rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 text-white font-bold text-sm shadow-xl shadow-indigo-600/30 transition-all flex items-center gap-2.5"
          >
            <Play className="w-4 h-4 fill-white" />
            Analyze & Debug Code
          </button>
        </div>
      </form>
    </div>
  );
};

export default NewReview;
