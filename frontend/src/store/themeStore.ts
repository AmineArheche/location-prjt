import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Theme = 'light' | 'dark' | 'system';

interface ThemeState {
  theme: Theme;
  resolvedTheme: 'light' | 'dark';
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  initTheme: () => void;
}

const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return 'dark';
};

const applyDocumentTheme = (resolved: 'light' | 'dark') => {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  if (resolved === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
  root.style.colorScheme = resolved;
};

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'dark',
      resolvedTheme: 'dark',

      setTheme: (newTheme: Theme) => {
        const resolved = newTheme === 'system' ? getSystemTheme() : newTheme;
        applyDocumentTheme(resolved);
        set({ theme: newTheme, resolvedTheme: resolved });
      },

      toggleTheme: () => {
        const { resolvedTheme } = get();
        const nextTheme = resolvedTheme === 'dark' ? 'light' : 'dark';
        applyDocumentTheme(nextTheme);
        set({ theme: nextTheme, resolvedTheme: nextTheme });
      },

      initTheme: () => {
        const { theme } = get();
        const resolved = theme === 'system' ? getSystemTheme() : theme;
        applyDocumentTheme(resolved);
        set({ resolvedTheme: resolved });

        // Listen to system changes if theme is system
        if (typeof window !== 'undefined' && window.matchMedia) {
          const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
          const handleChange = () => {
            if (get().theme === 'system') {
              const currentResolved = getSystemTheme();
              applyDocumentTheme(currentResolved);
              set({ resolvedTheme: currentResolved });
            }
          };
          mediaQuery.addEventListener('change', handleChange);
        }
      },
    }),
    {
      name: 'theme-storage',
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.initTheme();
        }
      },
    }
  )
);
