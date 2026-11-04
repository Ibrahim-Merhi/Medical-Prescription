# Source inventory

CSV exports are UTF-8 with optional BOM. Repeating child rows are grouped under the last non-empty parent ID. Production records are not bundled.


## Server scripts

|Name|State|DocType|Event/API|Destination|
|---|---|---|---|---|
|Reactivate Discharge Admission|Active||reactivate_discharge_admission|services / permissions / native form; see functionality matrix|
|delete test inpatient|Active||delete_test_inpatient_record|Review only: outside app scope|
|Update inpatient records|Active|Inpatient Record|Before Save|services / permissions / native form; see functionality matrix|
|HIS Patient Sync|Active||his_patient_sync|Review only: outside app scope|
|update all|Disabled|Medical Prescription|update_all_practitioner_display_names|Excluded: disabled|
|Fix DR names|Active|Healthcare Practitioner|Before Save|services / permissions / native form; see functionality matrix|
|DR uppper case|Disabled|Medical Prescription|fix_all_practitioner_names|Excluded: disabled|
|Patient Discharge Sync|Active|Patient|After Save|services / permissions / native form; see functionality matrix|
|update patient name|Disabled||fix_patient_names|Excluded: disabled|
|update patient status|Disabled||update_patient_admission_status|Excluded: disabled|
|discharge all|Disabled|Medical Prescription|discharge_all_except_icu|Excluded: disabled|
|sync inpatient service unit|Disabled||sync_inpatient_service_unit|Excluded: disabled|
|Check Patient Exists|Disabled||check_patient_exists|Excluded: disabled|
|Import HIS patient|Disabled||import_old_patient_v2|Excluded: disabled|
|Cancel inpatient records|Disabled||cancel_all_ip|Excluded: disabled|
|Delete ip|Disabled||delete_ip|Excluded: disabled|
|Upload|Disabled||import_old_patient|Excluded: disabled|
|MEd|Active|Medical Prescription|Before Insert|services / permissions / native form; see functionality matrix|
|Dr role|Active|Patient|Before Insert|services / permissions / native form; see functionality matrix|
|Doctor Role|Disabled|Patient|After Save|Excluded: disabled|
|Verify Nurse PIN|Active||verify_nurse_pin|services / permissions / native form; see functionality matrix|
|Set Nurse PIN|Active||set_my_nurse_pin|services / permissions / native form; see functionality matrix|
|Verify Double Signature|Active||verify_double_signature_nurse|services / permissions / native form; see functionality matrix|
|Patient|Active|Patient|Before Save|services / permissions / native form; see functionality matrix|
|Inpatient Record|Active|Inpatient Record|After Save|services / permissions / native form; see functionality matrix|
|Floor permision|Active|Medical Prescription|Before Insert|services / permissions / native form; see functionality matrix|
|Floor Assignment Plan|Active|Floor Assignment Plan|Before Save|services / permissions / native form; see functionality matrix|
|Duplicate Prescription New|Active||duplicate_medical_prescription|services / permissions / native form; see functionality matrix|
|Patient Encounter|Active|Patient Encounter|After Submit|services / permissions / native form; see functionality matrix|
|Duplicate Prescription|Disabled||duplicate_medical_prescription|Excluded: disabled|
|Medical Prescription Full|Active|Medical Prescription|Before Save|services / permissions / native form; see functionality matrix|
|Medical Presc|Active|Medical Prescription|After Save|services / permissions / native form; see functionality matrix|
|Schedule Medical Prescription|Disabled|Medical Prescription|Before Save|Excluded: disabled|
|Medical Prescriptionss|Disabled|Medical Prescription|Before Save|Excluded: disabled|
|old patient encounter|Disabled|Patient Encounter|After Submit|Excluded: disabled|
|Medical Prescription|Disabled|Patient Encounter|After Submit|Excluded: disabled|

### Server: Reactivate Discharge Admission

Fields referenced (syntactic scan): disabled, get, locked

Client APIs: None detected

### Server: delete test inpatient

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: Update inpatient records

Fields referenced (syntactic scan): get, patient, status

Client APIs: None detected

### Server: HIS Patient Sync

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: update all

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: Fix DR names

Fields referenced (syntactic scan): custom_display_name, first_name, get, meta, practitioner_name

Client APIs: None detected

### Server: DR uppper case

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: Patient Discharge Sync

Fields referenced (syntactic scan): get, name

Client APIs: None detected

### Server: update patient name

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: update patient status

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: discharge all

Fields referenced (syntactic scan): custom_service_unit, name

Client APIs: None detected

### Server: sync inpatient service unit

Fields referenced (syntactic scan): name, patient

Client APIs: None detected

### Server: Check Patient Exists

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: Import HIS patient

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: Cancel inpatient records

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: Delete ip

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: Upload

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: MEd

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: Dr role

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: Doctor Role

Fields referenced (syntactic scan): get, name

Client APIs: None detected

### Server: Verify Nurse PIN

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: Set Nurse PIN

Fields referenced (syntactic scan): enabled, nurse_user, pin, save

Client APIs: None detected

### Server: Verify Double Signature

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: Patient

Fields referenced (syntactic scan): custom_latest_case_number, get, name

Client APIs: None detected

### Server: Inpatient Record

Fields referenced (syntactic scan): custom_case_number, get, name, patient, status

Client APIs: None detected

### Server: Floor permision

Fields referenced (syntactic scan): 

Client APIs: None detected

### Server: Floor Assignment Plan

Fields referenced (syntactic scan): assignment_date, assignment_details, employee, name, shift

Client APIs: None detected

### Server: Duplicate Prescription New

Fields referenced (syntactic scan): get

Client APIs: None detected

### Server: Patient Encounter

Fields referenced (syntactic scan): custom_medical_prescription, get, name

Client APIs: None detected

### Server: Duplicate Prescription

Fields referenced (syntactic scan): get, name

Client APIs: None detected

### Server: Medical Prescription Full

Fields referenced (syntactic scan): administration_schedule, append, completed, disabled, doctype, dosage, double_signature_required, drug, drug_name, get, given, given_by, given_on, hold, idx, inpatient_record, is_phone_order, is_stopped_medicine, item_unique_key, items, locked, medication, name, phone_order_approved, prn, schedule_unique_key, scheduled_date, scheduled_time, second_signature_by, second_signature_done, second_signature_on, set, status, stay_duration_days, step_1_by, step_1_done, step_1_locked, step_1_on, step_2_by, step_2_done, step_2_on, stop_change

Client APIs: None detected

### Server: Medical Presc

Fields referenced (syntactic scan): get, name

Client APIs: None detected

### Server: Schedule Medical Prescription

Fields referenced (syntactic scan): append, dosage, drug, get, interval, interval_uom, items

Client APIs: None detected

### Server: Medical Prescriptionss

Fields referenced (syntactic scan): administration_schedule, completed, locked, step_2_done

Client APIs: None detected

### Server: old patient encounter

Fields referenced (syntactic scan): custom_medical_prescription, get, name

Client APIs: None detected

### Server: Medical Prescription

Fields referenced (syntactic scan): custom_medical_prescription, get, name

Client APIs: None detected

## Client scripts

|Name|State|DocType|Event/API|Destination|
|---|---|---|---|---|
|DR|Active|Healthcare Practitioner|Form|services / permissions / native form; see functionality matrix|
|Patient id remove|Active|Patient|List|services / permissions / native form; see functionality matrix|
|Hide navbar For Resident|Active|User|Form|Review only: outside app scope|
|Global|Disabled|DocType|Form|Excluded: disabled|
|Pin Code for User|Active|User|Form|Review only: outside app scope|
|Inpatient Record|Active|Inpatient Record|Form|services / permissions / native form; see functionality matrix|
|Patient|Active|Patient|Form|services / permissions / native form; see functionality matrix|
|Floor Assignment Plan|Active|Floor Assignment Plan|Form|services / permissions / native form; see functionality matrix|
|Patient Encounter|Active|Patient Encounter|Form|services / permissions / native form; see functionality matrix|
|css|Disabled|Medical Prescription|Form|Excluded: disabled|
|Medical Prescription|Active|Medical Prescription|Form|services / permissions / native form; see functionality matrix|

### Client: DR

Fields referenced (syntactic scan): first_name, last_name, middle_name

Client APIs: None detected

### Client: Patient id remove

Fields referenced (syntactic scan): 

Client APIs: None detected

### Client: Hide navbar For Resident

Fields referenced (syntactic scan): 

Client APIs: None detected

### Client: Global

Fields referenced (syntactic scan): 

Client APIs: None detected

### Client: Pin Code for User

Fields referenced (syntactic scan): name

Client APIs: set_my_nurse_pin

### Client: Inpatient Record

Fields referenced (syntactic scan): custom_discharge_status

Client APIs: None detected

### Client: Patient

Fields referenced (syntactic scan): active, admission_ordered_for, attending_practitioner, creation, custom_attending_practitioner, custom_case_number, custom_doctor_name, custom_floor, discharge_ordered_date, dosage, dosage_form, dose_number, dose_uom, drug, drug_name, frequency, inpatient_record, is_stopped, items, medical_department, medication, name, patient_name, practitioner, practitioner_name, read_only_primary, role_type, route, status, stop_change

Client APIs: frappe.client.get, frappe.client.get_list, frappe.client.set_value, reactivate_discharge_admission

### Client: Floor Assignment Plan

Fields referenced (syntactic scan): assigned_by, assignment_date

Client APIs: None detected

### Client: Patient Encounter

Fields referenced (syntactic scan): docstatus, encounter_date, encounter_time, floor, inpatient_record, medical_department, message, patient, practitioner, user_id

Client APIs: frappe.client.get, frappe.client.get_list, frappe.client.get_value, frappe.client.insert

### Client: css

Fields referenced (syntactic scan): administration_schedule, name, step_2_done

Client APIs: None detected

### Client: Medical Prescription

Fields referenced (syntactic scan): administration_schedule, allergies, comment, completed, creation, custom_time, dfg_estimated_mdrd, disabled, discharge_finalized, discharge_finalized_by, discharge_finalized_on, discharge_initiated, discharge_initiated_by, discharge_initiated_on, doctype, dosage, dose_number, dose_uom, double_signature_by, double_signature_on, double_signature_required, drug, drug_name, floor, frequency, given, hold, inpatient_record, interval_uom, is_latest_version, is_phone_order, is_stopped, is_stopped_medicine, item_unique_key, items, locked, medication, medications_sent, medications_sent_by, medications_sent_on, modified, name, owner, patient, patient_name, phone_order_approved, phone_order_approved_by, phone_order_created_by, phone_order_created_on, practitioner, practitioner_full_name, practitioner_name, prescription_date, prn, reason_of_delay, requested_doctor, route, schedule_unique_key, scheduled_date, scheduled_time, second_signature_by, second_signature_done, second_signature_on, status, step_1_by, step_1_done, step_1_locked, step_1_on, step_2_done, stop_change, stop_reason

Client APIs: duplicate_medical_prescription, frappe.client.get, frappe.client.get_list, frappe.client.save, verify_nurse_pin
