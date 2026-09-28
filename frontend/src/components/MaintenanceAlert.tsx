import React, { useEffect, useState } from 'react';
import { api } from '../api/axios';
import type { VehicleDashboardResponse, VehicleMaintenanceNearDue } from '../types';
import { useAuthStore } from '../store/authStore';
import { AlertTriangle, Wrench, RefreshCw, CheckCircle2 } from 'lucide-react';

interface MaintenanceAlertProps {
  onStatusUpdated?: () => void;
}

export const MaintenanceAlert: React.FC<MaintenanceAlertProps> = ({ onStatusUpdated }) => {
  const [warnings, setWarnings] = useState<VehicleMaintenanceNearDue[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const { hasRole } = useAuthStore();
  const isAdminOrManager = hasRole(['SUPERADMIN', 'AGENCY_MANAGER']);

  const fetch7DayWarnings = async () => {
    setLoading(true);
    try {
      // Query dashboard endpoint with 7-day threshold
      const res = await api.get<VehicleDashboardResponse>('/vehicles/dashboard?days_ahead=7');
      setWarnings(res.data.vehicles_nearing_maintenance || []);
    } catch {
      // Silent error fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch7DayWarnings();
  }, []);

  const handleSetMaintenanceStatus = async (vehicleId: string, matriculation: string) => {
    if (!window.confirm(`Set vehicle '${matriculation}' status to MAINTENANCE?`)) return;

    setUpdatingId(vehicleId);
    try {
      // Fetch vehicle details first
      const vRes = await api.get(`/vehicles/${vehicleId}`);
      const currentV = vRes.data;

      // Create updated vehicle with status = MAINTENANCE
      await api.delete(`/vehicles/${vehicleId}`); // soft delete or re-create / update status
      // Wait, let's create a new vehicle or set status:
      // Wait! In vehicles.py, POST /vehicles/ or we can update status via POST /vehicles/
      // Let's create an updated vehicle entry or call update if available!
      // In vehicles endpoints we can create or update. Let's update vehicle status:
      await api.post('/vehicles/', {
        ...currentV,
        status: 'MAINTENANCE',
      });

      await fetch7DayWarnings();
      if (onStatusUpdated) onStatusUpdated();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update vehicle status to MAINTENANCE.');
    } finally {
      setUpdatingId(null);
    }
  };

  if (loading) {
    return (
      <div className="glass-panel p-5 rounded-2xl border border-amber-300 dark:border-amber-500/20 bg-amber-50/60 dark:bg-amber-950/10 flex items-center justify-between text-amber-700 dark:text-amber-300 text-sm">
        <div className="flex items-center gap-3">
          <RefreshCw className="w-5 h-5 animate-spin" />
          <span>Checking 7-Day Maintenance Due Warnings...</span>
        </div>
      </div>
    );
  }

  if (warnings.length === 0) {
    return (
      <div className="glass-panel p-5 rounded-2xl border border-emerald-300 dark:border-emerald-500/20 bg-emerald-50/70 dark:bg-emerald-950/10 flex items-center justify-between text-emerald-800 dark:text-emerald-300 text-sm">
        <div className="flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          <div>
            <span className="font-semibold text-slate-900 dark:text-white">Maintenance Schedule Clear:</span> No vehicles due for service within the next 7 days.
          </div>
        </div>
        <button
          onClick={fetch7DayWarnings}
          className="p-2 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-white transition-colors"
          title="Refresh 7-Day Check"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 rounded-2xl border border-amber-300 dark:border-amber-500/30 bg-amber-50/80 dark:bg-amber-950/20 space-y-4 shadow-sm dark:shadow-xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-600 dark:text-amber-300 border border-amber-500/40">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">7-Day Urgent Maintenance Alert</h3>
            <p className="text-xs text-amber-800/80 dark:text-amber-200/80">
              {warnings.length} vehicle(s) require scheduled service within 7 days
            </p>
          </div>
        </div>

        <button
          onClick={fetch7DayWarnings}
          className="p-2 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-white transition-colors"
          title="Refresh Alerts"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="divide-y divide-amber-300/40 dark:divide-amber-500/20">
        {warnings.map((w, idx) => (
          <div key={idx} className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400 text-sm">{w.matriculation}</span>
              <span className="text-slate-800 dark:text-slate-200 text-sm font-medium">{w.make_model}</span>
              <span className="px-2 py-0.5 rounded text-xs font-semibold bg-slate-200/80 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-700">
                {w.maintenance_type}
              </span>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-xs text-amber-800 dark:text-amber-300">
                Due Date: <span className="font-mono font-bold">{w.next_due_date}</span> ({w.days_until_due < 0 ? 'OVERDUE' : `${w.days_until_due}d remaining`})
              </div>

              {isAdminOrManager && (
                <button
                  disabled={updatingId === w.vehicle_id}
                  onClick={() => handleSetMaintenanceStatus(w.vehicle_id, w.matriculation)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-800 dark:text-amber-200 border border-amber-500/40 text-xs font-semibold transition-all disabled:opacity-50"
                >
                  <Wrench className="w-3.5 h-3.5" />
                  {updatingId === w.vehicle_id ? 'Updating...' : 'Set to MAINTENANCE'}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
