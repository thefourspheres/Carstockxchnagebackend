-- Registration number on cars (admin only) so bulk upload can skip cars already in stock. Safe to re-run.
-- Run: sudo docker compose exec -T postgres psql -U postgres -d appdb -v ON_ERROR_STOP=1 < 004_car_registration.sql
BEGIN;
ALTER TABLE cars ADD COLUMN IF NOT EXISTS registration_number varchar(15);
CREATE UNIQUE INDEX IF NOT EXISTS ux_cars_org_reg ON cars (organization_id, registration_number)
  WHERE is_active AND registration_number IS NOT NULL;
COMMIT;
