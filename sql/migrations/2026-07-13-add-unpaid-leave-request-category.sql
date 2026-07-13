ALTER TABLE leave_requests
  MODIFY category ENUM(
    'paid leave',
    'health leave',
    'childcare sickness benefit',
    'childbirth leave',
    'exemption from obligation to work',
    'unpaid leave'
  ) NOT NULL;
