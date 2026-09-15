import React from 'react';
import { useAuthStore } from '../store/authStore';
import { LogOut, User as UserIcon } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuthStore();

  const getRoleBadgeColor = (role?: string) => {
    switch (role) {
      case 'SUPERADMIN':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      case 'AGENCY_MANAGER':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      default:
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
    }
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-900/30 font-bold text-white">
          M
        </div>
        <span className="font-semibold text-lg tracking-wide text-white">
          Morocco FleetManager
        </span>
      </div>

      {user && (
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3 px-3 py-1.5 rounded-lg bg-slate-800/60 border border-slate-700/50">
            <UserIcon className="w-4 h-4 text-slate-400" />
            <span className="text-sm font-medium text-slate-200">{user.email}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full border font-semibold ${getRoleBadgeColor(user.role)}`}>
              {user.role}
            </span>
          </div>

          <button
            onClick={logout}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500/20 transition-all text-sm font-medium"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>
      )}
    </header>
  );
};
