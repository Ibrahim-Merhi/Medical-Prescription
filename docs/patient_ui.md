# Patient reference layout

Patient list: Full Name, Medical File, Service Unit, Floor; matching standard filters,
without duplicate ID/status columns. Explicit saved named list layouts remain available.

Patient form: the supplied field order, demographics in two columns, practitioner grid
(Practitioner, Role Type, Specialty, Active), Medical & Admissions History, and Medical
Prescriptions tabs. Layout migration applies the selected presentation properties from
the supplied export, hides the empty Admissions tab, retains site-specific fields, and
leaves patient records, field types and permissions unchanged. Site presentation overrides
for the managed fields are replaced by these reference settings on migration.

Admissions history and prescriptions are paginated, permission-filtered tables with
same-tab Open actions, empty/error states and retries. Admission dates display the existing
admission_ordered_for and discharge_ordered_date fields; these are order dates, not independently
verified admission/discharge event timestamps. Medical file numbers remain text.

Create Prescription opens the native form with Patient and active Inpatient Record defaults.
Finalize Discharge requires a reason and confirmation and calls the existing backend service.
Both actions obey roles, native permissions, admission availability and existing staging
validation gates. This UI update does not enable unvalidated clinical workflows.

36 isolated tests, lint and JavaScript syntax checks pass. No live Frappe/browser visual test
has been performed here. After updating the dev server, compare all three tabs and list
columns, test history paging and restricted users, and verify the validated workflow actions.
The screenshot patient identities have not been copied into app data or tests.
