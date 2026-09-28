import React, { useEffect, useState } from 'react';
import { api } from '../api/axios';
import type { Vehicle, VehicleStatus } from '../types';
import { useAuthStore } from '../store/authStore';
import { Plus, Trash2, ShieldAlert, AlertCircle, RefreshCw } from 'lucide-react';

export const Vehicles: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('');

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [matriculation, setMatriculation] = useState('');
  const [makeModel, setMakeModel] = useState('');
  const [year, setYear] = useState(2024);
  const [currentMileage, setCurrentMileage] = useState(15000);
  const [dailyRateMad, setDailyRateMad] = useState(350);
  const [modalError, setModalError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { hasRole } = useAuthStore();
  const isAdminOrManager = hasRole(['SUPERADMIN', 'AGENCY_MANAGER']);

  const fetchVehicles = async () => {
    setLoading(true);
    setError('');
    try {
      const url = filterStatus ? `/vehicles/?status=${filterStatus}` : '/vehicles/';
      const res = await api.get<Vehicle[]>(url);
      setVehicles(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch vehicles list');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVehicles();
  }, [filterStatus]);

  const handleCreateVehicle = async (e: React.FormEvent) => {
    e.preventDefault();
    setModalError('');
    setSubmitting(true);

    try {
      await api.post('/vehicles/', {
        matriculation,
        make_model: makeModel,
        year: Number(year),
        current_mileage: Number(currentMileage),
        daily_rate_mad: Number(dailyRateMad),
        status: 'AVAILABLE',
      });

      setShowModal(false);
      setMatriculation('');
      setMakeModel('');
      fetchVehicles();
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to create vehicle. Check Moroccan plate format (e.g. 12345 | A | 15)';
      setModalError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteVehicle = async (id: string, mat: string) => {
    if (!window.confirm(`Are you sure you want to soft-delete vehicle '${mat}'?`)) return;

    try {
      await api.delete(`/vehicles/${id}`);
      fetchVehicles();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete vehicle. Admin/Manager permission required.');
    }
  };

  const getStatusBadge = (status: VehicleStatus) => {
    switch (status) {
      case 'AVAILABLE':
        return 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-500/40';
      case 'RENTED':
        return 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-500/40';
      case 'MAINTENANCE':
        return 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-300 border-amber-300 dark:border-amber-500/40';
      case 'RESERVED':
        return 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-300 border-purple-300 dark:border-purple-500/40';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Vehicle Fleet Management</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage rental inventory and Moroccan matriculation plates</p>
        </div>

        <div className="flex items-center gap-3">
          {/* Status Filter */}
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="glass-input rounded-xl px-3 py-2 text-sm bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 border-slate-300 dark:border-slate-700"
          >
            <option value="">All Statuses</option>
            <option value="AVAILABLE">AVAILABLE</option>
            <option value="RENTED">RENTED</option>
            <option value="MAINTENANCE">MAINTENANCE</option>
            <option value="RESERVED">RESERVED</option>
          </select>

          {/* Add Vehicle Button (Admin/Manager only) */}
          {isAdminOrManager ? (
            <button
              onClick={() => setShowModal(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white font-medium shadow-lg shadow-emerald-900/20 text-sm transition-all"
            >
              <Plus className="w-4 h-4" />
              Add Vehicle
            </button>
          ) : (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-xs text-slate-600 dark:text-slate-400">
              <ShieldAlert className="w-4 h-4 text-amber-500" />
              <span>AGENT Mode (Read-Only Actions)</span>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-500 dark:text-rose-400 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Table */}
      <div className="glass-panel rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-emerald-600 dark:text-emerald-400 flex items-center justify-center gap-3">
            <RefreshCw className="w-5 h-5 animate-spin" />
            <span>Loading Fleet Data...</span>
          </div>
        ) : vehicles.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-sm">
            No vehicles found in the fleet database.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600 dark:text-slate-300">
              <thead className="bg-slate-100/90 dark:bg-slate-900/90 text-xs font-semibold uppercase text-slate-600 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="px-6 py-4">Matriculation (Plate)</th>
                  <th className="px-6 py-4">Make & Model</th>
                  <th className="px-6 py-4">Year</th>
                  <th className="px-6 py-4">Mileage</th>
                  <th className="px-6 py-4">Daily Rate (MAD)</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60">
                {vehicles.map((v) => (
                  <tr key={v.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-mono font-bold text-emerald-600 dark:text-emerald-400">{v.matriculation}</td>
                    <td className="px-6 py-4 font-medium text-slate-900 dark:text-white">{v.make_model}</td>
                    <td className="px-6 py-4 text-slate-600 dark:text-slate-300">{v.year}</td>
                    <td className="px-6 py-4 text-slate-600 dark:text-slate-300">{v.current_mileage.toLocaleString()} km</td>
                    <td className="px-6 py-4 font-semibold text-teal-600 dark:text-teal-300">{v.daily_rate_mad} MAD</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getStatusBadge(v.status)}`}>
                        {v.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {isAdminOrManager ? (
                        <button
                          onClick={() => handleDeleteVehicle(v.id, v.matriculation)}
                          className="p-2 rounded-lg bg-rose-50 hover:bg-rose-100 dark:bg-rose-500/10 dark:hover:bg-rose-500/20 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-500/30 transition-all"
                          title="Soft Delete Vehicle"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      ) : (
                        <span className="text-xs text-slate-400 dark:text-slate-600 italic">Read-Only</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal for Creating Vehicle */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 dark:bg-black/75 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg glass-panel rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-2xl">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">Add New Vehicle to Fleet</h2>

            {modalError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-500 dark:text-rose-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{modalError}</span>
              </div>
            )}

            <form onSubmit={handleCreateVehicle} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Moroccan Matriculation Plate
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 12345 | A | 15 or 12345-A-15"
                  value={matriculation}
                  onChange={(e) => setMatriculation(e.target.value)}
                  className="w-full glass-input rounded-xl px-4 py-2 text-sm font-mono"
                />
                <span className="text-xs text-slate-500 mt-1 block">Validated against Moroccan plate standards</span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Make & Model
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Dacia Logan 1.5 dCi"
                  value={makeModel}
                  onChange={(e) => setMakeModel(e.target.value)}
                  className="w-full glass-input rounded-xl px-4 py-2 text-sm"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                    Year
                  </label>
                  <input
                    type="number"
                    required
                    value={year}
                    onChange={(e) => setYear(Number(e.target.value))}
                    className="w-full glass-input rounded-xl px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                    Mileage (km)
                  </label>
                  <input
                    type="number"
                    required
                    value={currentMileage}
                    onChange={(e) => setCurrentMileage(Number(e.target.value))}
                    className="w-full glass-input rounded-xl px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                    Rate (MAD/day)
                  </label>
                  <input
                    type="number"
                    required
                    value={dailyRateMad}
                    onChange={(e) => setDailyRateMad(Number(e.target.value))}
                    className="w-full glass-input rounded-xl px-3 py-2 text-sm font-bold text-emerald-600 dark:text-emerald-400"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 mt-6 pt-4 border-t border-slate-200 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-sm font-medium border border-slate-200 dark:border-transparent transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white font-medium text-sm shadow-lg shadow-emerald-900/20 transition-all"
                >
                  {submitting ? 'Saving...' : 'Save Vehicle'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
