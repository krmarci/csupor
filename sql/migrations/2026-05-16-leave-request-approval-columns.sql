ALTER TABLE leave_requests
  ADD COLUMN ceo_approved_by_id INT UNSIGNED NULL AFTER note,
  ADD COLUMN leadership_approved_by_id INT UNSIGNED NULL AFTER ceo_approved_by_id,
  ADD COLUMN decided_by_id INT UNSIGNED NULL AFTER leadership_approved_by_id,
  ADD KEY idx_leave_requests_ceo_approved_by_id (ceo_approved_by_id),
  ADD KEY idx_leave_requests_leadership_approved_by_id (leadership_approved_by_id),
  ADD KEY idx_leave_requests_decided_by_id (decided_by_id),
  ADD CONSTRAINT fk_leave_requests_ceo_approved_by_id
    FOREIGN KEY (ceo_approved_by_id) REFERENCES users(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  ADD CONSTRAINT fk_leave_requests_leadership_approved_by_id
    FOREIGN KEY (leadership_approved_by_id) REFERENCES users(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  ADD CONSTRAINT fk_leave_requests_decided_by_id
    FOREIGN KEY (decided_by_id) REFERENCES users(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE;
