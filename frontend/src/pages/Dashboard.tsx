import React, { useEffect, useState } from 'react';
import { api } from '../api/axios';
import type { VehicleDashboardResponse, Vehicle, VehicleStatus } from '../types';
import { MaintenanceAlert } from '../components/MaintenanceAlert';
import { BookingModal } from '../components/BookingModal';
import { Car, CheckCircle2, Key, Wrench, Clock, Plus, RefreshCw, AlertTriangle } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<VehicleDashboardResponse | null>(null);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');

  // Booking Modal State
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);
  const [selectedVehicleForBooking, setSelectedVehicleForBooking] = useState<string | undefined>(undefined);

  const fetchAllDashboardData = async () => {
    setLoading(true);
    setErrorMessage('');
    try {
      const [dashRes, vehRes] = await Promise.all([
        api.get<VehicleDashboardResponse>('/vehicles/dashboard?days_ahead=30'),
        api.get<Vehicle[]>('/vehicles/'),
      ]);
      setDashboardData(dashRes.data);
      setVehicles(vehRes.data);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || 'Failed to load fleet dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllDashboardData();
  }, []);

  const openBookingModalForVehicle = (vehicleId?: string) => {
    setSelectedVehicleForBooking(vehicleId);
    setIsBookingModalOpen(true);
  };

  const getVisualStatusBadge = (status: VehicleStatus) => {
    switch (status) {
      case 'AVAILABLE':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-bold';
      case 'RENTED':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40 font-bold';
      case 'MAINTENANCE':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40 font-bold';
      case 'RESERVED':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/40 font-bold';
    }
  };

  const summary = dashboardData?.status_summary;

  return (
    <div className="space-y-8">
      {/* Header & Quick Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Fleet Management Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">Real-time data table, 7-day maintenance alerts, and contract generation</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => openBookingModalForVehicle()}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white font-semibold text-sm shadow-lg shadow-emerald-900/30 transition-all"
          >
            <Plus className="w-4 h-4" />
            New Contract
          </button>
          <button
            onClick={fetchAllDashboardData}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all"
            title="Refresh Dashboard"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* 7-Day Urgent Maintenance Alert Widget */}
      <MaintenanceAlert onStatusUpdated={fetchAllDashboardData} />

      {/* Status Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Total Vehicles */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Fleet</span>
            <Car className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">{summary?.total_vehicles || 0}</div>
          <div className="text-xs text-slate-400 mt-1">Active Registered Vehicles</div>
        </div>

        {/* Available (GREEN) */}
        <div className="glass-panel p-5 rounded-2xl border border-emerald-500/30 bg-emerald-950/20">
          <div className="flex items-center justify-between text-emerald-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Available</span>
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-400">{summary?.available_count || 0}</div>
          <div className="text-xs text-emerald-300/80 mt-1">Green Status</div>
        </div>

        {/* Rented (RED) */}
        <div className="glass-panel p-5 rounded-2xl border border-rose-500/30 bg-rose-950/20">
          <div className="flex items-center justify-between text-rose-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Rented</span>
            <Key className="w-5 h-5" />
          </div>
          <div className="text-3xl font-extrabold text-rose-400">{summary?.rented_count || 0}</div>
          <div className="text-xs text-rose-300/80 mt-1">Red Status</div>
        </div>

        {/* Maintenance (AMBER) */}
        <div className="glass-panel p-5 rounded-2xl border border-amber-500/30 bg-amber-950/20">
          <div className="flex items-center justify-between text-amber-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Maintenance</span>
            <Wrench className="w-5 h-5" />
          </div>
          <div className="text-3xl font-extrabold text-amber-400">{summary?.maintenance_count || 0}</div>
          <div className="text-xs text-amber-300/80 mt-1">Amber Status</div>
        </div>

        {/* Reserved (PURPLE) */}
        <div className="glass-panel p-5 rounded-2xl border border-purple-500/30 bg-purple-950/20">
          <div className="flex items-center justify-between text-purple-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Reserved</span>
            <Clock className="w-5 h-5" />
          </div>
          <div className="text-3xl font-extrabold text-purple-400">{summary?.reserved_count || 0}</div>
          <div className="text-xs text-purple-300/80 mt-1">Purple Status</div>
        </div>
      </div>

      {/* Real-time Data Table of Vehicles */}
      <div className="glass-panel rounded-2xl border border-slate-800 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">Real-Time Vehicle Inventory Table</h2>
            <p className="text-xs text-slate-400">Live endpoint sync: `/vehicles/dashboard` & `/vehicles/`</p>
          </div>
          <span className="text-xs font-medium px-3 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
            {vehicles.length} Total Vehicles
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-emerald-400 flex items-center justify-center gap-3">
            <RefreshCw className="w-5 h-5 animate-spin" />
            <span>Syncing Real-Time Vehicle Table...</span>
          </div>
        ) : vehicles.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-sm">
            No vehicle data available in backend database.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-900/90 text-xs font-semibold uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Matriculation</th>
                  <th className="px-6 py-4">Make & Model</th>
                  <th className="px-6 py-4">Year</th>
                  <th className="px-6 py-4">Current Mileage</th>
                  <th className="px-6 py-4">Daily Rate</th>
                  <th className="px-6 py-4">Visual Status</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {vehicles.map((v) => (
                  <tr key={v.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-mono font-extrabold text-emerald-400">{v.matriculation}</td>
                    <td className="px-6 py-4 font-medium text-white">{v.make_model}</td>
                    <td className="px-6 py-4 text-slate-300">{v.year}</td>
                    <td className="px-6 py-4 text-slate-300">{v.current_mileage.toLocaleString()} km</td>
                    <td className="px-6 py-4 font-bold text-teal-300">{v.daily_rate_mad} MAD/day</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs border ${getVisualStatusBadge(v.status)}`}>
                        {v.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {v.status === 'AVAILABLE' ? (
                        <button
                          onClick={() => openBookingModalForVehicle(v.id)}
                          className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-semibold transition-all"
                        >
                          Book Now
                        </button>
                      ) : (
                        <span className="text-xs text-slate-500 italic">Unavailable</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Booking Modal Component */}
      <BookingModal
        isOpen={isBookingModalOpen}
        onClose={() => setIsBookingModalOpen(false)}
        onSuccess={fetchAllDashboardData}
        initialVehicleId={selectedVehicleForBooking}
      />
    </div>
  );
};
