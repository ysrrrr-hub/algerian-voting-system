-- Migration to add/standardize candidate columns
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS photo_url TEXT;
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS color VARCHAR(7) DEFAULT '#006233';
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS party_ar TEXT;
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS party_fr TEXT;
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS bio_ar TEXT;
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS bio_fr TEXT;
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS name_ar TEXT;
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS name_fr TEXT;

-- Best effort data migration
UPDATE candidates SET name_ar = full_name_ar WHERE name_ar IS NULL;
UPDATE candidates SET name_fr = full_name_fr WHERE name_fr IS NULL;
UPDATE candidates SET party_ar = party_name_ar WHERE party_ar IS NULL;
UPDATE candidates SET party_fr = party_name_fr WHERE party_fr IS NULL;
UPDATE candidates SET bio_ar = program_summary_ar WHERE bio_ar IS NULL;
UPDATE candidates SET bio_fr = program_summary_fr WHERE bio_fr IS NULL;

-- Cleanup (optional, but keeping original columns for safety unless sure)
