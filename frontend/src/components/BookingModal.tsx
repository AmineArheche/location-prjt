import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { api } from '../api/axios';
import type { Vehicle, Customer, BookingStatus, DamageReport } from '../types';
import { X, Calendar, DollarSign, UserCheck, AlertCircle } from 'lucide-react';
import { DamageInspector } from './DamageInspector';

const bookingSchema = z.object({
  vehicle_id: z.string().min(1, 'Please select a vehicle'),
  cin_or_passport: z.string().min(3, 'CIN or Passport number is required'),
  customer_name: z.string().min(2, 'Customer full name is required'),
  customer_phone: z.string().min(8, 'Valid phone number is required'),
  driver_license_number: z.string().min(4, 'Driver license number is required'),
  start_datetime: z.string().min(1, 'Start date & time is required'),
  end_datetime: z.string().min(1, 'End date & time is required'),
  start_mileage: z.number().min(0, 'Start mileage must be zero or positive'),
  deposit_amount: z.number().min(0, 'Deposit amount must be non-negative'),
  status: z.enum(['PENDING', 'ACTIVE'] as const),
}).refine((data) => {
  if (data.start_datetime && data.end_datetime) {
    return new Date(data.end_datetime) > new Date(data.start_datetime);
  }
  return true;
}, {
  message: 'End datetime must be strictly after Start datetime',
  path: ['end_datetime'],
});

type BookingFormValues = z.infer<typeof bookingSchema>;

interface BookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  initialVehicleId?: string;
}

export const BookingModal: React.FC<BookingModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  initialVehicleId,
}) => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [damageReport, setDamageReport] = useState<DamageReport>({ pins: [] });

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
    reset,
  } = useForm<BookingFormValues>({
    resolver: zodResolver(bookingSchema),
    defaultValues: {
      vehicle_id: initialVehicleId || '',
      cin_or_passport: '',
      customer_name: '',
      customer_phone: '',
      driver_license_number: '',
      start_datetime: '',
      end_datetime: '',
      start_mileage: 15000,
      deposit_amount: 2000,
      status: 'PENDING',
    },
  });

  const selectedVehicleId = watch('vehicle_id');
  const startDatetime = watch('start_datetime');
  const endDatetime = watch('end_datetime');
  const inputCin = watch('cin_or_passport');

  // Fetch Available Vehicles and Existing Customers
  useEffect(() => {
    if (isOpen) {
      setServerError('');
      setDamageReport({ pins: [] });
      api.get<Vehicle[]>('/vehicles/').then((res) => {
        setVehicles(res.data);
      }).catch(() => {});

      api.get<Customer[]>('/customers/').then((res) => {
        setCustomers(res.data);
      }).catch(() => {});

      if (initialVehicleId) {
        setValue('vehicle_id', initialVehicleId);
      }
    } else {
      reset();
    }
  }, [isOpen, initialVehicleId, setValue, reset]);

  // Auto-fill customer details if matching CIN is typed
  useEffect(() => {
    if (inputCin) {
      const match = customers.find(
        (c) => c.cin_or_passport.toLowerCase() === inputCin.trim().toLowerCase()
      );
      if (match) {
        setValue('customer_name', match.full_name);
        setValue('customer_phone', match.phone_number);
        setValue('driver_license_number', match.driver_license_number);
      }
    }
  }, [inputCin, customers, setValue]);

  // Calculate Dynamic Total Price (Daily Rate * Days)
  const selectedVehicle = vehicles.find((v) => v.id === selectedVehicleId);
  const calculateDynamicTotalPrice = (): number => {
    if (!selectedVehicle || !startDatetime || !endDatetime) return 0;
    const startMs = new Date(startDatetime).getTime();
    const endMs = new Date(endDatetime).getTime();
    if (isNaN(startMs) || isNaN(endMs) || endMs <= startMs) return 0;

    const diffHours = (endMs - startMs) / (1000 * 60 * 60);
    const days = Math.max(1, Math.ceil(diffHours / 24));
    return days * Number(selectedVehicle.daily_rate_mad);
  };

  const calculatedTotal = calculateDynamicTotalPrice();

  // Handle Form Submission
  const onSubmit = async (data: BookingFormValues) => {
    setServerError('');
    setIsSubmitting(true);

    try {
      // 1. Resolve or Create Customer by CIN
      let customerId = '';
      const existingCustomer = customers.find(
        (c) => c.cin_or_passport.toLowerCase() === data.cin_or_passport.trim().toLowerCase()
      );

      if (existingCustomer) {
        if (existingCustomer.is_blacklisted) {
          throw new Error(`Customer '${existingCustomer.full_name}' is BLACKLISTED and cannot rent vehicles.`);
        }
        customerId = existingCustomer.id;
      } else {
        // Create Customer
        const newCustRes = await api.post<Customer>('/customers/', {
          full_name: data.customer_name,
          phone_number: data.customer_phone,
          cin_or_passport: data.cin_or_passport,
          driver_license_number: data.driver_license_number,
          document_scans: { verified_by: 'Contract Form' },
          is_blacklisted: false,
        });
        customerId = newCustRes.data.id;
      }

      // 2. Submit Booking Transaction
      await api.post('/bookings/', {
        vehicle_id: data.vehicle_id,
        customer_id: customerId,
        start_datetime: new Date(data.start_datetime).toISOString(),
        end_datetime: new Date(data.end_datetime).toISOString(),
        start_mileage: data.start_mileage,
        total_price: calculatedTotal,
        deposit_amount: data.deposit_amount,
        status: data.status as BookingStatus,
        damage_report_start: damageReport,
      });

      onSuccess();
      onClose();
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Failed to create booking contract.';
      setServerError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;


  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="w-full max-w-2xl glass-panel rounded-2xl p-6 border border-slate-700 shadow-2xl my-8 relative">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <Calendar className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Create Rental Contract</h2>
              <p className="text-xs text-slate-400">Dynamic pricing & date-overlap verification</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {serverError && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{serverError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {/* Section 1: Vehicle & Dates */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
            <div className="text-xs font-semibold uppercase text-emerald-400 tracking-wider">
              1. Vehicle & Schedule Selection
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Select Vehicle
              </label>
              <select
                {...register('vehicle_id')}
                className="w-full glass-input rounded-xl px-4 py-2.5 text-sm bg-slate-900"
              >
                <option value="">-- Choose Vehicle --</option>
                {vehicles.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.matriculation} | {v.make_model} - {v.daily_rate_mad} MAD/day ({v.status})
                  </option>
                ))}
              </select>
              {errors.vehicle_id && (
                <p className="text-xs text-rose-400 mt-1">{errors.vehicle_id.message}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Start Date & Time
                </label>
                <input
                  type="datetime-local"
                  {...register('start_datetime')}
                  className="w-full glass-input rounded-xl px-3 py-2 text-sm bg-slate-900"
                />
                {errors.start_datetime && (
                  <p className="text-xs text-rose-400 mt-1">{errors.start_datetime.message}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  End Date & Time
                </label>
                <input
                  type="datetime-local"
                  {...register('end_datetime')}
                  className="w-full glass-input rounded-xl px-3 py-2 text-sm bg-slate-900"
                />
                {errors.end_datetime && (
                  <p className="text-xs text-rose-400 mt-1">{errors.end_datetime.message}</p>
                )}
              </div>
            </div>
          </div>

          {/* Section 2: Customer CIN & Information */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div className="text-xs font-semibold uppercase text-emerald-400 tracking-wider flex items-center gap-2">
                <UserCheck className="w-4 h-4" />
                2. Customer Details & CIN Verification
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  CIN / Passport Number *
                </label>
                <input
                  type="text"
                  placeholder="e.g. AB123456"
                  {...register('cin_or_passport')}
                  className="w-full glass-input rounded-xl px-3 py-2 text-sm font-mono uppercase"
                />
                {errors.cin_or_passport && (
                  <p className="text-xs text-rose-400 mt-1">{errors.cin_or_passport.message}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Customer Full Name *
                </label>
                <input
                  type="text"
                  placeholder="e.g. Youssef El Amrani"
                  {...register('customer_name')}
                  className="w-full glass-input rounded-xl px-3 py-2 text-sm"
                />
                {errors.customer_name && (
                  <p className="text-xs text-rose-400 mt-1">{errors.customer_name.message}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Phone Number *
                </label>
                <input
                  type="text"
                  placeholder="+212 661 234 567"
                  {...register('customer_phone')}
                  className="w-full glass-input rounded-xl px-3 py-2 text-sm"
                />
                {errors.customer_phone && (
                  <p className="text-xs text-rose-400 mt-1">{errors.customer_phone.message}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Driver License Number *
                </label>
                <input
                  type="text"
                  placeholder="DL-998877"
                  {...register('driver_license_number')}
                  className="w-full glass-input rounded-xl px-3 py-2 text-sm font-mono"
                />
                {errors.driver_license_number && (
                  <p className="text-xs text-rose-400 mt-1">{errors.driver_license_number.message}</p>
                )}
              </div>
            </div>
          </div>

          {/* Section 3: Financial & Mileage Calculation */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
            <div className="text-xs font-semibold uppercase text-emerald-400 tracking-wider flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              3. Dynamic Rate & Deposit Calculation
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Start Mileage (km)
                </label>
                <input
                  type="number"
                  {...register('start_mileage', { valueAsNumber: true })}
                  className="w-full glass-input rounded-xl px-3 py-2 text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Deposit Guarantee (MAD)
                </label>
                <input
                  type="number"
                  {...register('deposit_amount', { valueAsNumber: true })}
                  className="w-full glass-input rounded-xl px-3 py-2 text-sm text-teal-300 font-bold"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Initial Status
                </label>
                <select
                  {...register('status')}
                  className="w-full glass-input rounded-xl px-3 py-2 text-sm bg-slate-900"
                >
                  <option value="PENDING">PENDING (RESERVED)</option>
                  <option value="ACTIVE">ACTIVE (RENTED)</option>
                </select>
              </div>
            </div>

            {/* Dynamic Price Display Banner */}
            <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/30 flex items-center justify-between">
              <div>
                <div className="text-xs text-emerald-300 font-medium">Calculated Contract Total</div>
                <div className="text-xs text-slate-400 mt-0.5">
                  {selectedVehicle ? `${selectedVehicle.daily_rate_mad} MAD/day` : 'Select vehicle'}
                </div>
              </div>
              <div className="text-2xl font-extrabold text-emerald-400 font-mono">
                {calculatedTotal.toLocaleString()} MAD
              </div>
            </div>
          </div>

          {/* Section 4: Vehicle Damage Inspector Map */}
          <DamageInspector
            value={damageReport}
            onChange={setDamageReport}
            title="Initial Check-In Damage Inspector"
          />

          {/* Footer Buttons */}

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium transition-all"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white font-semibold text-sm shadow-lg shadow-emerald-900/30 transition-all disabled:opacity-50"
            >
              {isSubmitting ? 'Creating Contract...' : 'Create Contract'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
