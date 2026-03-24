CREATE DATABASE IF NOT EXISTS csupor
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE csupor;

CREATE TABLE IF NOT EXISTS users (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  email VARCHAR(120) NOT NULL,
  username VARCHAR(50) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  privilege ENUM('employee', 'hr', 'ceo', 'developer') NOT NULL DEFAULT 'employee',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_email (email),
  UNIQUE KEY uq_users_username (username)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user_profiles (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id INT UNSIGNED NOT NULL,
  full_name VARCHAR(120) NULL,
  name_at_birth VARCHAR(120) NULL,
  date_of_birth DATE NULL,
  place_of_birth VARCHAR(120) NULL,
  gender ENUM('male', 'female', 'other') NULL,
  mothers_maiden_name VARCHAR(120) NULL,
  citizenships VARCHAR(255) NULL,
  social_security_number CHAR(9) NULL,
  tax_number CHAR(10) NULL,
  education_number CHAR(11) NULL,
  teacher_id_card_number VARCHAR(64) NULL,
  permanent_residence VARCHAR(255) NULL,
  temporary_address VARCHAR(255) NULL,
  phone_number VARCHAR(40) NULL,
  bank_account_number VARCHAR(64) NULL,
  marital_status VARCHAR(64) NULL,
  disability VARCHAR(255) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_user_profiles_user_id (user_id),
  CONSTRAINT fk_user_profiles_user_id
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT chk_user_profiles_ssn_digits
    CHECK (social_security_number IS NULL OR social_security_number REGEXP '^[0-9]{9}$'),
  CONSTRAINT chk_user_profiles_tax_digits
    CHECK (tax_number IS NULL OR tax_number REGEXP '^[0-9]{10}$'),
  CONSTRAINT chk_user_profiles_education_digits
    CHECK (education_number IS NULL OR education_number REGEXP '^[0-9]{11}$')
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dependents (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id INT UNSIGNED NOT NULL,
  name VARCHAR(120) NOT NULL,
  date_of_birth DATE NOT NULL,
  social_security_number CHAR(9) NOT NULL,
  dependency_start DATE NOT NULL,
  disability VARCHAR(255) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_dependents_user_id (user_id),
  CONSTRAINT fk_dependents_user_id
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT chk_dependents_ssn_digits
    CHECK (social_security_number REGEXP '^[0-9]{9}$')
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS educational_qualifications (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id INT UNSIGNED NOT NULL,
  level_or_type VARCHAR(120) NOT NULL,
  qualification_name VARCHAR(120) NOT NULL,
  institution_name VARCHAR(120) NOT NULL,
  degree_number VARCHAR(80) NOT NULL,
  year_obtained SMALLINT UNSIGNED NOT NULL,
  highest TINYINT(1) NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_educational_qualifications_user_id (user_id),
  KEY idx_educational_qualifications_highest (user_id, highest),
  CONSTRAINT fk_educational_qualifications_user_id
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT chk_educational_qualifications_year
    CHECK (year_obtained BETWEEN 1900 AND 9999)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS professional_exams (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id INT UNSIGNED NOT NULL,
  qualification_name VARCHAR(120) NOT NULL,
  year_obtained SMALLINT UNSIGNED NOT NULL,
  degree_number VARCHAR(80) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_professional_exams_user_id (user_id),
  CONSTRAINT fk_professional_exams_user_id
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT chk_professional_exams_year
    CHECK (year_obtained BETWEEN 1900 AND 9999)
) ENGINE=InnoDB;

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
