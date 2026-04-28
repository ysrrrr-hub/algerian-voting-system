-- migrations/elections_v2.sql

-- First, map the current status if it's 'PRELIMINARY' to 'OPEN'
UPDATE elections SET status = 'OPEN' WHERE status = 'PRELIMINARY';

ALTER TABLE elections ADD COLUMN IF NOT EXISTS official_close_date timestamptz;
ALTER TABLE elections ADD COLUMN IF NOT EXISTS official_close_by VARCHAR(100);
ALTER TABLE elections ADD COLUMN IF NOT EXISTS pv_generated_at timestamptz;
ALTER TABLE elections ADD COLUMN IF NOT EXISTS pv_url VARCHAR(500);
ALTER TABLE elections ADD COLUMN IF NOT EXISTS turnout_percent numeric(5,2);
ALTER TABLE elections ADD COLUMN IF NOT EXISTS final_winner_id integer;
ALTER TABLE elections ADD COLUMN IF NOT EXISTS notes text;

-- Add check constraint for election status
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_election_status'
  ) THEN
    ALTER TABLE elections ADD CONSTRAINT chk_election_status CHECK (status IN ('DRAFT','SCHEDULED','OPEN','PRELIMINARY','CLOSED','CANCELLED'));
  END IF;
END $$;
