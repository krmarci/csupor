CREATE TABLE IF NOT EXISTS leave_requests (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT UNSIGNED NOT NULL,
  contract_id INT NOT NULL,
  category ENUM(
    'paid leave',
    'health leave',
    'childcare sickness benefit',
    'childbirth leave',
    'exemption from obligation to work',
    'unpaid leave'
  ) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NULL,
  status ENUM(
    'pending approval',
    'approved',
    'rejected',
    'pending cancellation',
    'cancelled'
  ) NOT NULL DEFAULT 'pending approval',
  note TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_leave_requests_user_contract (user_id, contract_id),
  KEY idx_leave_requests_dates (start_date, end_date),
  KEY idx_leave_requests_status (status),
  CONSTRAINT fk_leave_requests_user_id
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_leave_requests_contract_id
    FOREIGN KEY (contract_id) REFERENCES contracts(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT chk_leave_requests_date_order
    CHECK (end_date IS NULL OR end_date >= start_date)
) ENGINE=InnoDB;
