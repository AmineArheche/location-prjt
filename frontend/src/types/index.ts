export type UserRole = 'SUPERADMIN' | 'AGENCY_MANAGER' | 'AGENT';

export type VehicleStatus = 'AVAILABLE' | 'RENTED' | 'MAINTENANCE' | 'RESERVED';

export type BookingStatus = 'PENDING' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED';

export type MaintenanceType = 'VIDANGE' | 'VISITE_TECHNIQUE' | 'ASSURANCE' | 'REPAIR';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  agency_location?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Customer {
  id: string;
  full_name: string;
  phone_number: string;
  cin_or_passport: string;
  driver_license_number: string;
  document_scans?: Record<string, any>;
  is_blacklisted: boolean;
  created_at: string;
  updated_at: string;
}

export interface Vehicle {
  id: string;
  matriculation: string;
  make_model: string;
  year: number;
  current_mileage: number;
  daily_rate_mad: number;
  status: VehicleStatus;
  created_at: string;
  updated_at: string;
}

export interface Booking {
  id: string;
  vehicle_id: string;
  customer_id: string;
  agent_id: string;
  start_datetime: string;
  end_datetime: string;
  start_mileage: number;
  end_mileage?: number;
  total_price: number;
  deposit_amount: number;
  status: BookingStatus;
  damage_report_start?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface MaintenanceLog {
  id: string;
  vehicle_id: string;
  type: MaintenanceType;
  date_performed: string;
  next_due_date: string;
  cost: number;
  created_at: string;
  updated_at: string;
}

export interface VehicleStatusAggregate {
  total_vehicles: number;
  available_count: number;
  rented_count: number;
  maintenance_count: number;
  reserved_count: number;
}

export interface VehicleMaintenanceNearDue {
  vehicle_id: string;
  matriculation: string;
  make_model: string;
  maintenance_type: MaintenanceType;
  next_due_date: string;
  days_until_due: number;
}

export interface VehicleDashboardResponse {
  status_summary: VehicleStatusAggregate;
  vehicles_nearing_maintenance: VehicleMaintenanceNearDue[];
}

export type DamageType = 'Scratch' | 'Dent' | 'Crack' | 'Broken Light';
export type DamageSeverity = 'Minor' | 'Moderate' | 'Severe';

export interface DamagePin {
  id: string;
  view: 'Front' | 'Back' | 'Left Side' | 'Right Side' | 'Top' | 'Windshield';
  x: number; // relative % coordinates (0-100)
  y: number; // relative % coordinates (0-100)
  type: DamageType;
  severity: DamageSeverity;
  photoUrl?: string;
  notes?: string;
}

export interface DamageReport {
  pins: DamagePin[];
  notes?: string;
  timestamp?: string;
}

