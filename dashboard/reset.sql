DELETE FROM votes;
DELETE FROM blockchain WHERE block_index > 0;
DELETE FROM vote_receipts;
UPDATE voters SET has_voted = false;
SELECT COUNT(*) AS remaining_votes FROM votes;
SELECT COUNT(*) AS voters_who_voted FROM voters WHERE has_voted = true;
