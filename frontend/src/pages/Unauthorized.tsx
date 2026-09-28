import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

export const Unauthorized: React.FC = () => {
  const { user } = useAuthStore();

  return (
    <div className="min-h-[70vh] flex items-center justify-center">
      <div className="max-w-md w-full glass-panel rounded-2xl p-8 border border-slate-200 dark:border-slate-800 text-center shadow-xl dark:shadow-2xl">
        <div className="p-3 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-500 dark:text-rose-400 w-fit mx-auto mb-4">
          <ShieldAlert className="w-10 h-10" />
        </div>
        
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">403 - Access Restricted</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
          Your current role (<span className="text-emerald-600 dark:text-emerald-400 font-semibold">{user?.role}</span>) does not have sufficient permissions to view this resource or perform this operation.
        </p>

        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-white font-medium text-sm border border-slate-200 dark:border-slate-700 transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
};
