ALTER TABLE leadership
  ADD COLUMN position ENUM('principal', 'deputy principal') NOT NULL DEFAULT 'principal' AFTER contract_id;
