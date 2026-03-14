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
