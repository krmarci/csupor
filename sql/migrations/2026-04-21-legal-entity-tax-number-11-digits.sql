ALTER TABLE legal_entities
  DROP CONSTRAINT chk_legal_entities_tax_number_digits;
  
ALTER TABLE legal_entities
  MODIFY COLUMN tax_number CHAR(11) NOT NULL;
  
UPDATE legal_entities
SET tax_number = CONCAT(tax_number, '0');

ALTER TABLE legal_entities
  ADD CONSTRAINT chk_legal_entities_tax_number_digits
    CHECK (tax_number REGEXP '^[0-9]{11}$');