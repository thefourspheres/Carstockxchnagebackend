-- Add Owner and Kilometer to cars. Safe to re-run.
-- Run: sudo docker compose exec -T postgres psql -U postgres -d appdb -v ON_ERROR_STOP=1 < 003_car_owner_km.sql
BEGIN;
ALTER TABLE cars ADD COLUMN IF NOT EXISTS owner smallint;
ALTER TABLE cars ADD COLUMN IF NOT EXISTS kilometer integer;
ALTER TABLE cars DROP CONSTRAINT IF EXISTS cars_owner_km_chk;
ALTER TABLE cars ADD CONSTRAINT cars_owner_km_chk
  CHECK ((owner IS NULL OR owner BETWEEN 1 AND 10) AND (kilometer IS NULL OR kilometer BETWEEN 0 AND 2000000));
COMMIT;
