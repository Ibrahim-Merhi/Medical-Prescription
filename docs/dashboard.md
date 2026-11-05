# Medical dashboard and census reports

Open Medical Dashboard from the Medical Prescription sidebar, or `/app/medical-overview`.
It becomes the first sidebar item on upgrade. Existing sidebar entries are retained;
repeated migrations do not create duplicate dashboard or report links.

## Metrics and definitions

- Visible patients: all Patient rows readable by the current user, including historical patients.
- Current inpatients: distinct patients on non-cancelled Inpatient Records whose status is
  Admitted or Discharge Scheduled, also restricted to readable Patient rows.
- Scheduled admissions: distinct visible patients with Admission Scheduled records; these
  are not counted as current inpatients.
- Scheduled discharges: distinct current patients with Discharge Scheduled records.
- Inpatients without floor: current patients with a blank Inpatient Record.custom_floor.
- Floor chart and table: current distinct patients per recorded custom_floor. Blank values
  appear as Unassigned. Floors with no current visible patients are omitted.
- Prescription chart: non-cancelled prescription records grouped by business status, all
  versions included, intersected with readable patients. Hidden when prescription read access
  is absent. This is not a medication count or a latest-version patient count.

Patient counts are not available-bed counts or capacity percentages. The floor value is
whatever is recorded on the admission; the dashboard does not infer location from old
prescriptions or independently validate transfers. Duplicate active admissions trigger a
warning, and a patient recorded on multiple floors is counted once per floor but only once
in the overall inpatient total.

## Reports

Medical Floor Census: floor, distinct current patients, active admission records and
scheduled discharges, plus a bar chart. Optional floor filter.

Medical Inpatient Census: links to admission and patient records, recorded floor and status.
Optional floor and status filters. Enter Unassigned to select blank floors. Report tooling
provides native printing/export subject to Frappe permissions. Both reports are current
census reports, not historical occupancy snapshots.

## Permissions and performance

Both Patient and Inpatient Record read access are required. Each dataset is read through
frappe.get_list, retaining native User Permissions and installed permission query hooks.
Inpatient and prescription rows are additionally intersected with readable patient IDs.
The endpoint does not accept a user identity or arbitrary DocType. No permission-bypassing
SQL, global aggregate cache, or prepared reports are used. Do not loosen patient permissions
to make hospital-wide counts visible: users see their authorized scope only.

Reads paginate in batches of 2,000 with no silent record limit. Large patient registries can
make refresh slow; benchmark on the development site before wider rollout. Refresh is manual
and on page opening; the server timestamp indicates the request time. Sequential database
reads are not an atomic hospital-wide snapshot.

## Validation and rollout

32 isolated Python tests passed, including duplicate admission accounting, visibility
intersection, missing floors, denied permissions, pagination and idempotent sidebar upgrade.
Python lint, JavaScript syntax and package builds passed. Real Frappe migration, browser
rendering, actual SQL permission enforcement and report export still require dev-site checks.

After pushing the Medical Prescription repository, pull main, migrate, build the app,
clear cache and restart. Open the dashboard as Administrator and a restricted nurse; compare
counts with native lists. Test empty data, scheduled admission, admitted/discharge-scheduled
patients, blank floors and duplicate admissions. Confirm reports and links remain in the
same Desk tab and repeated migration does not duplicate sidebar entries.

## Unified sidebar

The Medical Prescription sidebar now groups the dashboard, census reports, Patients,
Inpatient Records, Patient Encounters, Appointments, Vital Signs, Prescriptions,
Medications, drug Items, dosage/duration masters, Healthcare Practitioners, Employees,
Floor Assignment Plans, Floors, both prescription and Healthcare Service Units,
Service Unit Types, Medical Departments, app/Healthcare Settings and Users.

Only existing non-child DocTypes are linked. Employee is a staff directory, not a
filtered nurse-only directory; nurse allocation uses Floor Assignment Plan. Doctors
use Healthcare Practitioner. Native record permissions apply to every destination.

Child tables (medication items/schedules, past drugs, assigned doctors and floor
assignment details) stay within their parent forms. Nurse PIN is credential storage
with no list permissions and is deliberately excluded from the sidebar.

Migration refreshes the app-owned sections and retains unrelated local entries under
Additional Links. Managed link labels, order and grouping follow the app definitions.
Repeated migrations do not duplicate entries.
