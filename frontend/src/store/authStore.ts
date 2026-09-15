import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, UserRole } from '../types';

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
  hasRole: (allowedRoles: UserRole[]) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,

      setAuth: (token: string, user: User) => {
        localStorage.setItem('access_token', token);
        set({ token, user, isAuthenticated: true });
      },

      logout: () => {
        localStorage.removeItem('access_token');
        set({ token: null, user: null, isAuthenticated: false });
      },

      hasRole: (allowedRoles: UserRole[]) => {
        const { user } = get();
        if (!user) return false;
        return allowedRoles.includes(user.role);
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
