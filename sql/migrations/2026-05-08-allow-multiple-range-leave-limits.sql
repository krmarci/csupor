ALTER TABLE contract_leave_limits
  DROP INDEX uq_leave_limit_scope,
  ADD KEY idx_contract_leave_limits_scope (contract_id, calendar_year, leave_type);
