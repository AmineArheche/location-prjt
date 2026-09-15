import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Car, CalendarCheck } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

export const Sidebar: React.FC = () => {
  const { hasRole } = useAuthStore();
  const isAdminOrManager = hasRole(['SUPERADMIN', 'AGENCY_MANAGER']);

  const navItems = [
    { to: '/dashboard', label: 'Fleet Dashboard', icon: LayoutDashboard },
    { to: '/vehicles', label: 'Vehicle Fleet', icon: Car },
    { to: '/bookings', label: 'Bookings', icon: CalendarCheck },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/60 p-4 flex flex-col gap-2 min-h-[calc(100vh-4rem)]">
      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-3 mb-2">
        Main Menu
      </div>

      {navItems.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`
            }
          >
            <Icon className="w-4 h-4" />
            {item.label}
          </NavLink>
        );
      })}

      {isAdminOrManager && (
        <div className="mt-6">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-3 mb-2">
            Administration
          </div>
          <div className="px-3 py-2 text-xs font-medium text-purple-400 bg-purple-500/10 rounded-lg border border-purple-500/20">
            Manager Access Granted
          </div>
        </div>
      )}
    </aside>
  );
};
