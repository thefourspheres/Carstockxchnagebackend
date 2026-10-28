-- Track whether the welcome email reached the employee. Safe to re-run.
-- Run: sudo docker compose exec -T postgres psql -U postgres -d appdb -v ON_ERROR_STOP=1 < 002_employee_invite.sql
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'employees' AND column_name = 'invite_sent_at') THEN
    ALTER TABLE employees ADD COLUMN invite_sent_at timestamptz;
    -- Existing employees already got their login, so mark them as sent (first run only).
    UPDATE employees SET invite_sent_at = COALESCE(created_at, now());
  END IF;
END $$;
