-- Simplify cars to the 12 admin fields. Safe to re-run.
-- Run: sudo docker compose exec -T postgres psql -U postgres -d appdb -v ON_ERROR_STOP=1 < 001_simplify_cars.sql
BEGIN;

ALTER TABLE cars ADD COLUMN IF NOT EXISTS condition        varchar(30);
ALTER TABLE cars ADD COLUMN IF NOT EXISTS description      text;
ALTER TABLE cars ADD COLUMN IF NOT EXISTS actual_price     numeric(12,2);
ALTER TABLE cars ADD COLUMN IF NOT EXISTS discounted_price numeric(12,2);
ALTER TABLE cars ADD COLUMN IF NOT EXISTS status           varchar(20);

-- Carry over old prices if the old columns still exist.
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='cars' AND column_name='saleprice') THEN
    UPDATE cars SET actual_price     = COALESCE(actual_price, saleprice, price),
                    discounted_price = COALESCE(discounted_price, bottomprice)
     WHERE actual_price IS NULL;
  END IF;
END $$;

UPDATE cars SET condition = COALESCE(condition, 'Used'),
                status    = COALESCE(status, CASE WHEN is_active THEN 'Available' ELSE 'Draft' END),
                name      = COALESCE(name, 'Untitled'),
                brand     = COALESCE(brand, 'Unknown'),
                year      = COALESCE(year, EXTRACT(YEAR FROM now())::int),
                actual_price = COALESCE(actual_price, 1);
UPDATE cars SET discounted_price = NULL WHERE discounted_price >= actual_price;

ALTER TABLE cars
  DROP COLUMN IF EXISTS kilometer, DROP COLUMN IF EXISTS price,
  DROP COLUMN IF EXISTS saleprice, DROP COLUMN IF EXISTS bottomprice,
  DROP COLUMN IF EXISTS engine_specs, DROP COLUMN IF EXISTS dimensions,
  DROP COLUMN IF EXISTS capacity_fuel, DROP COLUMN IF EXISTS suspension,
  DROP COLUMN IF EXISTS tyres, DROP COLUMN IF EXISTS features,
  DROP COLUMN IF EXISTS exteriors_lights_rating, DROP COLUMN IF EXISTS core_systems_rating,
  DROP COLUMN IF EXISTS supporting_systems_rating, DROP COLUMN IF EXISTS interiors_ac_rating,
  DROP COLUMN IF EXISTS inspection_rating, DROP COLUMN IF EXISTS insurance_type,
  DROP COLUMN IF EXISTS registration_number, DROP COLUMN IF EXISTS registration_year,
  DROP COLUMN IF EXISTS insurance_valid_until, DROP COLUMN IF EXISTS ownership,
  DROP COLUMN IF EXISTS rto;

ALTER TABLE cars
  ALTER COLUMN name SET NOT NULL, ALTER COLUMN brand SET NOT NULL,
  ALTER COLUMN year SET NOT NULL, ALTER COLUMN condition SET NOT NULL,
  ALTER COLUMN actual_price SET NOT NULL, ALTER COLUMN status SET NOT NULL,
  ALTER COLUMN status SET DEFAULT 'Available',
  ALTER COLUMN is_active SET NOT NULL,
  ALTER COLUMN car_type TYPE varchar(30);

ALTER TABLE cars DROP CONSTRAINT IF EXISTS cars_status_chk;
ALTER TABLE cars ADD CONSTRAINT cars_status_chk CHECK (status IN ('Available','Reserved','Sold','Draft'));
ALTER TABLE cars DROP CONSTRAINT IF EXISTS cars_price_chk;
ALTER TABLE cars ADD CONSTRAINT cars_price_chk CHECK (actual_price > 0 AND (discounted_price IS NULL OR discounted_price < actual_price));

CREATE INDEX IF NOT EXISTS ix_cars_org_status ON cars (organization_id, status);

COMMIT;
