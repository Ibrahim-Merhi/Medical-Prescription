# API reference

All paths are under `medical_prescription.api`. Mutations accept authenticated
POST requests, with Frappe session/CSRF behavior and transaction boundaries.

|Method|Arguments|Result / legacy mapping|
|---|---|---|
|duplicate_medical_prescription|source_name, new_prescription_date|New name; replaces active duplicate API; repeated same source/date returns existing result|
|set_my_nurse_pin|pin|success; replaces set_my_nurse_pin; self only|
|record_administration|prescription, schedule_row, action, optional second_nurse, pin, reason|success; step_1 or step_2; second signer verified within the write transaction|
|finalize_discharge|inpatient_record, reason|Updated status/count; supports admissions with no prescription|
|reactivate_discharge_admission|inpatient_record, reason|Reopens latest linked prescription only; rejects a second active admission|
|patient_prescriptions|patient, optional start/page_length|Permission-filtered list; GET; maximum 100 rows|

`verify_nurse_pin` and `verify_double_signature_nurse` are not exposed as separate
identity proofs. A browser-returned identity is insufficient authorization for a
later signature write. PIN verification now belongs to `record_administration`.
The password-based alternate signature API is not migrated.

Errors raise Frappe exceptions and leave the request transaction to roll back.
No endpoint returns a PIN/hash. Mutation success is returned only after checks and
writes; no endpoint commits mid-operation. Database/Redis failures propagate.

