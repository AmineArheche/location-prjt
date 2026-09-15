from enum import Enum


class UserRole(str, Enum):
    SUPERADMIN = "SUPERADMIN"
    AGENCY_MANAGER = "AGENCY_MANAGER"
    AGENT = "AGENT"


class VehicleStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RENTED = "RENTED"
    MAINTENANCE = "MAINTENANCE"
    RESERVED = "RESERVED"


class BookingStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class MaintenanceType(str, Enum):
    VIDANGE = "VIDANGE"
    VISITE_TECHNIQUE = "VISITE_TECHNIQUE"
    ASSURANCE = "ASSURANCE"
    REPAIR = "REPAIR"


class SubscriptionPlan(str, Enum):
    STARTER = "STARTER"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"

