import React, { useEffect, useState } from 'react';
import { api } from '../api/axios';
import type { Booking, Vehicle, Customer, BookingStatus } from '../types';
import { Plus, AlertCircle, RefreshCw, FileText } from 'lucide-react';

export const Bookings: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const handleDownloadPdf = (bookingId: string) => {
    api.get(`/bookings/${bookingId}/pdf`, { responseType: 'blob' }).then((res) => {
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
    }).catch((err) => {
      alert('Failed to generate PDF contract: ' + (err.response?.data?.detail || err.message));
    });
  };


  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [selectedVehicleId, setSelectedVehicleId] = useState('');
  const [selectedCustomerId, setSelectedCustomerId] = useState('');
  const [startDatetime, setStartDatetime] = useState('');
  const [endDatetime, setEndDatetime] = useState('');
  const [startMileage, setStartMileage] = useState(1000);
  const [totalPrice, setTotalPrice] = useState(1200);
  const [depositAmount, setDepositAmount] = useState(2000);
  const [status, setStatus] = useState<BookingStatus>('PENDING');
  const [modalError, setModalError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const [resB, resV, resC] = await Promise.all([
        api.get<Booking[]>('/bookings/'),
        api.get<Vehicle[]>('/vehicles/'),
        api.get<Customer[]>('/customers/'),
      ]);
      setBookings(resB.data);
      setVehicles(resV.data);
      setCustomers(resC.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load bookings data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateBooking = async (e: React.FormEvent) => {
    e.preventDefault();
    setModalError('');
    setSubmitting(true);

    try {
      await api.post('/bookings/', {
        vehicle_id: selectedVehicleId,
        customer_id: selectedCustomerId,
        start_datetime: new Date(startDatetime).toISOString(),
        end_datetime: new Date(endDatetime).toISOString(),
        start_mileage: Number(startMileage),
        total_price: Number(totalPrice),
        deposit_amount: Number(depositAmount),
        status,
        damage_report_start: { scratches: [], notes: 'Inspected prior to checkout' },
      });

      setShowModal(false);
      fetchData();
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to create booking transaction.';
      setModalError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (bStatus: BookingStatus) => {
    switch (bStatus) {
      case 'ACTIVE':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      case 'PENDING':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/40';
      case 'COMPLETED':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
      case 'CANCELLED':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Booking Reservations</h1>
          <p className="text-sm text-slate-400 mt-1">Transactional booking manager with date-overlap & customer blacklist protection</p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white font-medium shadow-lg shadow-emerald-900/30 text-sm transition-all"
        >
          <Plus className="w-4 h-4" />
          Create New Booking
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Bookings Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-emerald-400 flex items-center justify-center gap-3">
            <RefreshCw className="w-5 h-5 animate-spin" />
            <span>Loading Bookings...</span>
          </div>
        ) : bookings.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-sm">
            No bookings recorded yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-900/90 text-xs font-semibold uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Booking ID</th>
                  <th className="px-6 py-4">Start Time</th>
                  <th className="px-6 py-4">End Time</th>
                  <th className="px-6 py-4">Total Price (MAD)</th>
                  <th className="px-6 py-4">Deposit (MAD)</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {bookings.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4 font-mono text-xs text-slate-400">{b.id.substring(0, 8)}...</td>
                    <td className="px-6 py-4 text-slate-200">{new Date(b.start_datetime).toLocaleString()}</td>
                    <td className="px-6 py-4 text-slate-200">{new Date(b.end_datetime).toLocaleString()}</td>
                    <td className="px-6 py-4 font-semibold text-emerald-400">{b.total_price} MAD</td>
                    <td className="px-6 py-4 text-teal-300">{b.deposit_amount} MAD</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getStatusBadge(b.status)}`}>
                        {b.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleDownloadPdf(b.id)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 text-sky-400 text-xs font-medium transition-all"
                        title="Download French Legal Contract PDF"
                      >
                        <FileText className="w-3.5 h-3.5" />
                        <span>PDF Contract</span>
                      </button>
                    </td>
                  </tr>
                ))}

              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal for Creating Booking */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg glass-panel rounded-2xl p-6 border border-slate-700 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-white mb-2">Create New Booking</h2>
            <p className="text-xs text-slate-400 mb-4">Atomic transaction: Verifies vehicle availability, customer blacklist status, and updates fleet state</p>

            {modalError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{modalError}</span>
              </div>
            )}

            <form onSubmit={handleCreateBooking} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Select Vehicle (AVAILABLE status required)
                </label>
                <select
                  required
                  value={selectedVehicleId}
                  onChange={(e) => setSelectedVehicleId(e.target.value)}
                  className="w-full glass-input rounded-xl px-4 py-2.5 text-sm bg-slate-900"
                >
                  <option value="">-- Select Vehicle --</option>
                  {vehicles.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.matriculation} - {v.make_model} ({v.status})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Select Customer
                </label>
                <select
                  required
                  value={selectedCustomerId}
                  onChange={(e) => setSelectedCustomerId(e.target.value)}
                  className="w-full glass-input rounded-xl px-4 py-2.5 text-sm bg-slate-900"
                >
                  <option value="">-- Select Customer --</option>
                  {customers.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.full_name} ({c.cin_or_passport}) {c.is_blacklisted ? '[BLACKLISTED]' : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    Start Date & Time
                  </label>
                  <input
                    type="datetime-local"
                    required
                    value={startDatetime}
                    onChange={(e) => setStartDatetime(e.target.value)}
                    className="w-full glass-input rounded-xl px-3 py-2 text-sm bg-slate-900"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    End Date & Time
                  </label>
                  <input
                    type="datetime-local"
                    required
                    value={endDatetime}
                    onChange={(e) => setEndDatetime(e.target.value)}
                    className="w-full glass-input rounded-xl px-3 py-2 text-sm bg-slate-900"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    Start Mileage
                  </label>
                  <input
                    type="number"
                    required
                    value={startMileage}
                    onChange={(e) => setStartMileage(Number(e.target.value))}
                    className="w-full glass-input rounded-xl px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    Total (MAD)
                  </label>
                  <input
                    type="number"
                    required
                    value={totalPrice}
                    onChange={(e) => setTotalPrice(Number(e.target.value))}
                    className="w-full glass-input rounded-xl px-3 py-2 text-sm font-bold text-emerald-400"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    Deposit (MAD)
                  </label>
                  <input
                    type="number"
                    required
                    value={depositAmount}
                    onChange={(e) => setDepositAmount(Number(e.target.value))}
                    className="w-full glass-input rounded-xl px-3 py-2 text-sm text-teal-300"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Initial Booking Status
                </label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value as BookingStatus)}
                  className="w-full glass-input rounded-xl px-4 py-2 text-sm bg-slate-900"
                >
                  <option value="PENDING">PENDING (Sets vehicle status to RESERVED)</option>
                  <option value="ACTIVE">ACTIVE (Sets vehicle status to RENTED)</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-3 mt-6 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white font-medium text-sm shadow-lg shadow-emerald-900/30 transition-all"
                >
                  {submitting ? 'Processing Transaction...' : 'Confirm Booking'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
