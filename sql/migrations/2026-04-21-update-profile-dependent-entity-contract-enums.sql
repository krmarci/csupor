UPDATE user_profiles
SET marital_status = CASE
  WHEN marital_status IS NULL OR TRIM(marital_status) = '' THEN NULL
  WHEN LOWER(TRIM(marital_status)) IN ('single', 'unmarried') THEN 'single'
  WHEN LOWER(TRIM(marital_status)) IN ('married') THEN 'married'
  WHEN LOWER(TRIM(marital_status)) IN ('divorced') THEN 'divorced'
  WHEN LOWER(TRIM(marital_status)) IN ('widowed') THEN 'widowed'
  WHEN LOWER(TRIM(marital_status)) IN ('civil partnership', 'civil_partner', 'civil partner') THEN 'civil partnership'
  ELSE NULL
END;

ALTER TABLE user_profiles
  MODIFY COLUMN marital_status ENUM('single', 'married', 'divorced', 'widowed', 'civil partnership') NULL;

ALTER TABLE dependents
  ADD COLUMN dependent_type ENUM('child', 'other dependent') NOT NULL DEFAULT 'child' AFTER name;

ALTER TABLE legal_entities
  ADD COLUMN tax_number CHAR(10) NULL AFTER om_id;

UPDATE legal_entities
SET tax_number = COALESCE(tax_number, '0000000000')
WHERE tax_number IS NULL;

ALTER TABLE legal_entities
  MODIFY COLUMN tax_number CHAR(10) NOT NULL,
  ADD CONSTRAINT chk_legal_entities_tax_number_digits
    CHECK (tax_number REGEXP '^[0-9]{10}$');

UPDATE contracts
SET contract_type = CASE contract_type
  WHEN 'pedagogue' THEN 'Teacher'
  WHEN 'assistant in educational and training work' THEN 'Teaching Assistant'
  WHEN 'employee according to the Labour Code' THEN 'Employee under the Labour Code'
  ELSE contract_type
END;

ALTER TABLE contracts
  MODIFY COLUMN contract_type ENUM('Teacher', 'Teaching Assistant', 'Nursery Assistant', 'Secretary', 'Employee under the Labour Code') NOT NULL;
