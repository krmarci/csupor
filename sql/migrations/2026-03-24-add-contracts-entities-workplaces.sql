CREATE TABLE IF NOT EXISTS legal_entities (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  address VARCHAR(255) NOT NULL,
  om_id CHAR(6) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT chk_legal_entities_om_id_digits
    CHECK (om_id REGEXP '^[0-9]{6}$')
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS places_of_work (
  id INT NOT NULL AUTO_INCREMENT,
  legal_entity_id INT NOT NULL,
  address VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_places_of_work_legal_entity_id (legal_entity_id),
  CONSTRAINT fk_places_of_work_legal_entity_id
    FOREIGN KEY (legal_entity_id) REFERENCES legal_entities(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS contracts (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT UNSIGNED NOT NULL,
  contract_type ENUM('pedagogue', 'assistant in educational and training work', 'employee according to the Labour Code') NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NULL,
  certificate_of_good_conduct_number VARCHAR(64) NULL,
  certificate_of_good_conduct_date DATE NULL,
  job_title VARCHAR(120) NOT NULL,
  working_hours_per_week INT NOT NULL,
  teacher_classification ENUM('Trainee', 'Teacher I', 'Teacher II', 'Master Teacher', 'Research Teacher') NULL,
  classification_start_date DATE NULL,
  legal_entity_id INT NOT NULL,
  place_of_work_id INT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_contracts_user_id (user_id),
  KEY idx_contracts_legal_entity_id (legal_entity_id),
  KEY idx_contracts_place_of_work_id (place_of_work_id),
  CONSTRAINT fk_contracts_user_id
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_contracts_legal_entity_id
    FOREIGN KEY (legal_entity_id) REFERENCES legal_entities(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk_contracts_place_of_work_id
    FOREIGN KEY (place_of_work_id) REFERENCES places_of_work(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT chk_contracts_working_hours_positive
    CHECK (working_hours_per_week > 0),
  CONSTRAINT chk_contracts_date_order
    CHECK (end_date IS NULL OR end_date >= start_date)
) ENGINE=InnoDB;
