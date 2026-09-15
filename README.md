# LocationProject - Enterprise Car Rental Fleet Management Platform

**LocationProject** is a production-grade, full-stack enterprise web application designed for car rental agencies in Morocco. It features a high-throughput **FastAPI** backend with **SQLAlchemy 2.0 (Async)**, **Alembic migrations**, **PostgreSQL / SQLite** dual database compatibility, **Pydantic v2** schema validation, and a modern **React (Vite + TypeScript)** frontend styled with **Tailwind CSS v3** and managed via **Zustand**.

---

## 🏛️ System Architecture

```
                       ┌──────────────────────────────────────────┐
                       │          React (Vite + TS) SPA           │
                       │   Tailwind CSS v3 | Lucide | Zustand     │
                       └────────────────────┬─────────────────────┘
                                            │
                                  Axios JWT Interceptor
                                  (Auto Bearer / 401 Guard)
                                            │
                                            ▼
                       ┌──────────────────────────────────────────┐
                       │          FastAPI Async REST API          │
                       │    (OAuth2 Bearer + RBAC Middleware)     │
                       └────────────────────┬─────────────────────┘
                                            │
                                  SQLAlchemy 2.0 Async
                                  Alembic DB Migrations
                                            │
                                            ▼
                       ┌──────────────────────────────────────────┐
                       │   PostgreSQL / SQLite Dual Compatibility │
                       │    JSONB / UUID4 / UTC Timezone Models   │
                       └──────────────────────────────────────────┘
```

---

## 🔐 User Roles & Grants Matrix (RBAC Comparison)

The platform enforces strict **Role-Based Access Control (RBAC)** at both the FastAPI backend middleware layer (`RoleChecker`) and the React client route layer (`ProtectedRoute`).

| Feature / Action | `SUPERADMIN` | `AGENCY_MANAGER` | `AGENT` |
| :--- | :---: | :---: | :---: |
| **System Overview & Fleet Dashboard** | ✅ Read | ✅ Read | ✅ Read |
| **Create Rental Contracts / Bookings** | ✅ Write | ✅ Write | ✅ Write |
| **Read Vehicle Fleet & Statuses** | ✅ Read | ✅ Read | ✅ Read |
| **Read Customer Records & CIN Details** | ✅ Read | ✅ Read | ✅ Read |
| **Create New Customer Profiles** | ✅ Write | ✅ Write | ✅ Write |
| **Add New Vehicles to Inventory** | ✅ Write | ✅ Write | ❌ Restricted |
| **Soft-Delete Vehicles / Fleet Items** | ✅ Write | ✅ Write | ❌ Restricted |
| **Update User Roles (`AGENT` ➔ `MANAGER`)** | ✅ Write | ✅ Write | ❌ Restricted |
| **Trigger 7-Day Urgent Maintenance Schedule** | ✅ Write | ✅ Write | ❌ Restricted |
| **Soft-Delete Bookings & Contracts** | ✅ Write | ✅ Write | ✅ Write |

### Role Definitions
1. **`SUPERADMIN`**: System superuser with unrestricted access across all agency locations, user management, fleet creation, role assignment, and audit capabilities.
2. **`AGENCY_MANAGER`**: Agency branch administrator permitted to manage local fleet inventory, soft-delete vehicles, transition vehicle maintenance states, and update staff member details.
3. **`AGENT`**: Front-desk desk operator responsible for handling daily customer check-in/check-out, reading fleet availability, creating rental contracts, and verifying customer CIN credentials.

---

## 🚗 Core Features & Functionalities

### 1. Moroccan License Plate Validation System
Built with specialized regex matching and normalization to parse all standard Moroccan vehicle matriculation formats:
- **Standard 3-Part Series**: `"12345 | A | 15"`, `"12345-A-15"`, `"12345 / A / 15"`, `"12345 | أ | 15"` ➔ Automatically normalized to `"12345 | A | 15"`.
- **Temporary Series**: `"WW-12345"`, `"ww 12345"` ➔ Normalized to `"WW-12345"`.
- **Official Series**: `"MA-12345"` ➔ Normalized to `"MA-12345"`.
- Throws descriptive Pydantic `ValueError` on invalid plate inputs.

### 2. Transactional Booking Engine & Double-Booking Prevention
The `POST /api/v1/bookings/` endpoint wraps reservation workflows inside atomic database transactions:
- **Customer Blacklist Guard**: Rejects booking creation if `customer.is_blacklisted` is `True` (`HTTP 400 Bad Request`).
- **Vehicle Status Guard**: Verifies `vehicle.status == VehicleStatus.AVAILABLE` (`HTTP 400 Bad Request`).
- **Date Overlap Query**: Executes an optimized interval overlap query:
  $$\text{Overlap} \iff (\text{booking.start} < \text{new.end}) \land (\text{booking.end} > \text{new.start})$$
  Returns `HTTP 409 Conflict` if double-booking is detected.
- **Fleet State Auto-Update**: Updates vehicle status to `RENTED` (if booking status is `ACTIVE`) or `RESERVED` (if booking status is `PENDING`).

### 3. Dynamic Contract Price Calculation
Integrated into the frontend `BookingModal` using **React Hook Form** and **Zod**:
- Calculates contract duration in days:
  $$\text{Days} = \max\left(1, \left\lceil \frac{\text{end\_ms} - \text{start\_ms}}{1000 \times 60 \times 60 \times 24} \right\rceil\right)$$
- Computes total in real-time: $\text{Total MAD} = \text{Days} \times \text{daily\_rate\_mad}$.

### 4. 7-Day Urgent Maintenance Warnings Widget
Queries `/api/v1/vehicles/dashboard?days_ahead=7` to highlight vehicles with upcoming oil changes (*vidange*), technical inspections (*visite technique*), or insurance renewals due within 7 days or overdue. Includes a manager quick-action button to transition vehicle status to `MAINTENANCE`.

### 5. Soft-Delete & Audit Base Model Architecture
All database entities inherit from `Base` in `app/db/base_class.py`:
- `id`: UUID4 primary key.
- `created_at`: UTC timezone timestamp (`func.now()`).
- `updated_at`: UTC timezone timestamp (`func.now()`, `onupdate=func.now()`).
- `deleted_at`: Nullable UTC timestamp for soft deletes (`soft_delete()`, `restore()`).

---

## 🗄️ Database Models & Schema

```
  ┌───────────────────┐            ┌───────────────────┐
  │       User        │            │     Customer      │
  ├───────────────────┤            ├───────────────────┤
  │ id (UUID4 PK)     │            │ id (UUID4 PK)     │
  │ email (Unique)    │            │ full_name         │
  │ password_hash     │            │ phone_number      │
  │ role (Enum)       │            │ cin_or_passport   │
  │ agency_location   │            │ driver_license    │
  │ is_active         │            │ document_scans    │
  └─────────┬─────────┘            │ is_blacklisted    │
            │                      └─────────┬─────────┘
            │                                │
            │      ┌───────────────────┐     │
            └─────►│      Booking      │◄────┘
                   ├───────────────────┤
                   │ id (UUID4 PK)     │
                   │ vehicle_id (FK)───┼──────────┐
                   │ customer_id (FK)  │          │
                   │ agent_id (FK)     │          │
                   │ start_datetime    │          │
                   │ end_datetime      │          │
                   │ total_price       │          │
                   │ deposit_amount    │          │
                   │ status (Enum)     │          │
                   │ damage_report     │          │
                   └───────────────────┘          │
                                                  │
                                                  ▼
                                           ┌───────────────┐
                                           │    Vehicle    │
                                           ├───────────────┤
                                           │ id (UUID4 PK) │
                                           │ matriculation │
                                           │ make_model    │
                                           │ year, mileage │
                                           │ daily_rate    │
                                           │ status (Enum) │
                                           └───────┬───────┘
                                                   │
                                                   ▼
                                           ┌───────────────┐
                                           │  Maintenance  │
                                           ├───────────────┤
                                           │ id (UUID4 PK) │
                                           │ vehicle_id FK │
                                           │ type (Enum)   │
                                           │ date_performed│
                                           │ next_due_date │
                                           │ cost          │
                                           └───────────────┘
```

---

## 📡 REST API Catalog (16 Endpoints)

| Module | Method | Endpoint | Access Level | Description |
| --- | --- | --- | --- | --- |
| **Health** | `GET` | `/` | Public | Application welcome & OpenAPI metadata |
| | `GET` | `/health` | Public | System status health check |
| **Auth** | `POST` | `/api/v1/auth/register` | Public | Register new user account |
| | `POST` | `/api/v1/auth/login` | Public | Authenticate user & issue OAuth2 Bearer token |
| | `GET` | `/api/v1/auth/me` | Bearer Token | Get current user profile |
| **Users** | `GET` | `/api/v1/users/` | Manager / Admin | List all registered staff accounts |
| | `GET` | `/api/v1/users/{id}` | Bearer Token | Get user details by UUID |
| | `PATCH` | `/api/v1/users/{id}` | Manager / Admin | Update user role (`AGENT` ➔ `MANAGER`) or status |
| | `DELETE` | `/api/v1/users/{id}` | Manager / Admin | Soft delete user record |
| **Vehicles**| `GET` | `/api/v1/vehicles/dashboard` | Bearer Token | Real-time status summary & maintenance warnings |
| | `GET` | `/api/v1/vehicles/` | Bearer Token | List all active vehicles (supports status filter) |
| | `POST` | `/api/v1/vehicles/` | Manager / Admin | Add vehicle with Moroccan plate validation |
| | `GET` | `/api/v1/vehicles/{id}` | Bearer Token | Get vehicle details by UUID |
| | `DELETE` | `/api/v1/vehicles/{id}` | Manager / Admin | Soft delete vehicle entry |
| **Bookings**| `GET` | `/api/v1/bookings/` | Bearer Token | List all active booking contracts |
| | `POST` | `/api/v1/bookings/` | Bearer Token | Create booking (Atomic transaction + Overlap check) |
| | `GET` | `/api/v1/bookings/{id}` | Bearer Token | Get booking details by UUID |
| | `DELETE` | `/api/v1/bookings/{id}` | Bearer Token | Soft delete booking record |
| **Maint.** | `GET` | `/api/v1/maintenance/` | Bearer Token | List maintenance logs |
| | `POST` | `/api/v1/maintenance/` | Bearer Token | Log vehicle maintenance service record |
| | `GET` | `/api/v1/maintenance/{id}`| Bearer Token | Get maintenance log details by UUID |
| | `DELETE` | `/api/v1/maintenance/{id}`| Bearer Token | Soft delete maintenance log |

---

## 🔑 Demo Test Credentials

The database contains pre-configured test users, vehicles, and customer records:

| Role | Email | Password | Access Rights |
| --- | --- | --- | --- |
| **SUPERADMIN** | `superadmin@agency.ma` | `adminpassword123` | Unrestricted global access, role management, fleet deletion |
| **AGENCY_MANAGER** | `manager@agency.ma` | `managerpassword123` | Agency manager rights, fleet management, maintenance alerts |
| **AGENT** | `agent@agency.ma` | `agentpassword123` | Front-desk rights: contract creation, customer lookup, fleet view |

---

## 🚀 Quick Setup & Installation Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### 2. Backend Setup & Seed Data
```bash
# Navigate to project root
cd locationproject

# Activate Python Virtual Environment
.\venv\Scripts\activate

# Seed demo users, vehicles, customers, and maintenance warnings
python seed_demo.py

# Launch FastAPI backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Backend Base URL**: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`

### 3. Frontend Setup & Launch
```bash
# Navigate to frontend folder
cd locationproject\frontend

# Launch React Vite dev server
npm run dev
```
- **Frontend App URL**: `http://localhost:5173`

---

## 🧪 Production Verification

- **TypeScript Compilation (`npx tsc --noEmit`)**: Passed with 0 errors.
- **Vite Production Bundle (`npm run build`)**: Generated `dist/` bundle cleanly (323 kB JS, 17.7 kB CSS).
- **Backend Test Suite**: Verified against OpenAPI 3.0 schema and Alembic migration pipelines.
