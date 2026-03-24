-- Normalize existing blank profile values to NULL so CHECK constraints remain valid
-- when optional fields are intentionally left empty.

UPDATE user_profiles
SET
  full_name = NULLIF(TRIM(full_name), ''),
  name_at_birth = NULLIF(TRIM(name_at_birth), ''),
  place_of_birth = NULLIF(TRIM(place_of_birth), ''),
  mothers_maiden_name = NULLIF(TRIM(mothers_maiden_name), ''),
  citizenships = NULLIF(TRIM(citizenships), ''),
  social_security_number = NULLIF(TRIM(social_security_number), ''),
  tax_number = NULLIF(TRIM(tax_number), ''),
  education_number = NULLIF(TRIM(education_number), ''),
  teacher_id_card_number = NULLIF(TRIM(teacher_id_card_number), ''),
  permanent_residence = NULLIF(TRIM(permanent_residence), ''),
  temporary_address = NULLIF(TRIM(temporary_address), ''),
  phone_number = NULLIF(TRIM(phone_number), ''),
  bank_account_number = NULLIF(TRIM(bank_account_number), ''),
  marital_status = NULLIF(TRIM(marital_status), ''),
  disability = NULLIF(TRIM(disability), '');
