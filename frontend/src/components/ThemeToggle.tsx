import React from 'react';
import { Sun, Moon, Laptop } from 'lucide-react';
import { useThemeStore, type Theme } from '../store/themeStore';

interface ThemeToggleProps {
  className?: string;
  variant?: 'simple' | 'dropdown' | 'segmented';
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ className = '', variant = 'simple' }) => {
  const { theme, resolvedTheme, setTheme, toggleTheme } = useThemeStore();

  if (variant === 'segmented') {
    const options: { value: Theme; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
      { value: 'light', label: 'Light', icon: Sun },
      { value: 'dark', label: 'Dark', icon: Moon },
      { value: 'system', label: 'System', icon: Laptop },
    ];

    return (
      <div className={`inline-flex items-center p-1 rounded-xl bg-slate-200/80 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700/60 shadow-inner ${className}`}>
        {options.map(({ value, label, icon: Icon }) => {
          const isActive = theme === value;
          return (
            <button
              key={value}
              type="button"
              onClick={() => setTheme(value)}
              title={`${label} theme`}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-white dark:bg-slate-700 text-emerald-600 dark:text-emerald-400 shadow-sm font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{label}</span>
            </button>
          );
        })}
      </div>
    );
  }

  // Simple toggle button between light & dark
  const isDark = resolvedTheme === 'dark';

  return (
    <button
      type="button"
      onClick={toggleTheme}
      title={isDark ? 'Passer au mode clair' : 'Passer au mode sombre'}
      aria-label="Toggle theme"
      className={`relative p-2 rounded-xl border transition-all duration-300 group ${
        isDark
          ? 'bg-slate-800/80 hover:bg-slate-800 text-amber-400 border-slate-700/60 hover:border-amber-400/40 shadow-sm'
          : 'bg-white hover:bg-slate-100 text-slate-700 border-slate-200 hover:border-slate-300 shadow-sm'
      } ${className}`}
    >
      <div className="relative w-5 h-5 flex items-center justify-center">
        <Sun
          className={`w-5 h-5 absolute transition-all duration-300 transform ${
            isDark
              ? 'opacity-100 rotate-0 scale-100 text-amber-400'
              : 'opacity-0 -rotate-90 scale-50'
          }`}
        />
        <Moon
          className={`w-5 h-5 absolute transition-all duration-300 transform ${
            isDark
              ? 'opacity-0 rotate-90 scale-50'
              : 'opacity-100 rotate-0 scale-100 text-indigo-600'
          }`}
        />
      </div>
    </button>
  );
};
