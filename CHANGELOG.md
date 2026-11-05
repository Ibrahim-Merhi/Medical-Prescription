# Changelog

## 0.1.0a1 — Local development alpha

- Reconstructed scoped app metadata and portable print branding.
- Added modular permission, prescription, duplication, PIN, administration,
  floor and discharge services with explicit validation gates.
- Added isolated checks, source inventory, conflict reports and release blockers.
- Not a completed migration or production release; see docs/validation_gates.md.


## Medical dashboard and census reports

- Added current patient/inpatient KPIs, floor census and prescription-status charts.
- Added floor and inpatient census Script Reports with permission-filtered data.
- Added dashboard-first sidebar navigation; preserves existing links on migration.
- Added duplicate-admission and unassigned-floor indicators plus isolated regression tests.

## Unified clinical sidebar

- Grouped dashboard, reports, patient care, medicines, staff, floor/unit masters and settings in one Desk sidebar.
- Added existing-DocType checks and preserved unrelated local links across repeated migrations.

## Patient reference screens

- Applied reference list columns, filters, demographics/tab layout and practitioner grid.
- Added permission-filtered admission/prescription histories with pagination and same-tab links.
- Connected Create Prescription and Finalize Discharge buttons to existing gated workflows.
