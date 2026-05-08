CREATE TABLE IF NOT EXISTS contract_leave_limits (
  id INT NOT NULL AUTO_INCREMENT,
  contract_id INT NOT NULL,
  calendar_year SMALLINT UNSIGNED NOT NULL,
  leave_type ENUM(
    'basic leave',
    'supplementary leave based on age',
    'supplementary leave for children',
    'supplementary leave for children with disability',
    'supplementary leave for young employees',
    'supplementary leave for employees with reduced working capacity / eligible for disability benefits',
    'sick leave',
    'leave carried over from previous year',
    'maternity leave',
    'paternity leave',
    'parental leave',
    'childcare fee',
    'childcare allowance',
    'supplementary leave for the birth of a grandchild',
    'supplementary leave for first marriage',
    'exemption from obligation to work'
  ) NOT NULL,
  limit_days INT NOT NULL,
  period_start DATE NULL,
  period_end DATE NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_leave_limit_scope (contract_id, calendar_year, leave_type),
  KEY idx_contract_leave_limits_contract (contract_id),
  CONSTRAINT fk_contract_leave_limits_contract_id
    FOREIGN KEY (contract_id) REFERENCES contracts(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT chk_contract_leave_limits_non_negative
    CHECK (limit_days >= 0),
  CONSTRAINT chk_contract_leave_limits_date_order
    CHECK (period_end IS NULL OR period_start IS NULL OR period_end >= period_start)
) ENGINE=InnoDB;
