CREATE TABLE IF NOT EXISTS leadership (
  id INT NOT NULL AUTO_INCREMENT,
  legal_entity_id INT NOT NULL,
  contract_id INT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_leadership_legal_entity_id (legal_entity_id),
  KEY idx_leadership_contract_id (contract_id),
  CONSTRAINT fk_leadership_legal_entity_id
    FOREIGN KEY (legal_entity_id) REFERENCES legal_entities(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk_leadership_contract_id
    FOREIGN KEY (contract_id) REFERENCES contracts(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT chk_leadership_date_order
    CHECK (end_date IS NULL OR end_date >= start_date)
) ENGINE=InnoDB;
