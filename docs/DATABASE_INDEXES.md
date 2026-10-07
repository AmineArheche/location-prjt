# Guide d'Optimisation des Index SQL

- `vehicles(license_plate)` : Clé unique d'immatriculation.
- `bookings(vehicle_id, start_datetime, end_datetime)` : Index composite de recherche de disponibilité.
- `maintenance_logs(vehicle_id, service_date)` : Index d'historique de révision.
