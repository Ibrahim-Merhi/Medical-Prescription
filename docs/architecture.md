# Architecture and extension guide

`medical_prescription/hooks.py` owns app identity, dependency declarations,
form assets, document events and permission hooks. The module is named Medical
Prescription, so source-owned DocTypes are separate from Healthcare's module.

`medical_prescription/medical_prescription/doctype/` contains the eleven exported
DocTypes and the branding singleton. Original field identifiers, Link targets,
child relationships and naming-series options are retained. Added fields are
documented in the missing-components report. Standard Healthcare DocTypes are
dependencies, never copied into this module.

`domain.py` contains independently testable legacy period parsing, nursing grid,
frequency spacing and duplication decisions. The grid supplies selectable slots;
it does not calculate the number of doses clinically indicated.

`services/` separates prescription validation/versioning, duplication, nursing
administration, signatures, floor validation and discharge. `api.py` supplies
authenticated endpoints. Services own authorization so calling a service from
another server function does not omit access checks. Request transactions belong
to Frappe; no API commits manually. Admission row locks serialize prescription
chains. Patient locks serialize discharge across admissions.

`permissions.py` supplies the same row predicates to list and direct-access checks.
Patient hooks extend existing patient visibility and therefore require a full
Healthcare permission regression on staging. Native User Permissions remain active.

`install.py` checks dependencies and conflicts before configuration writes;
configuration is installed only when missing. Local customizations are not
silently overwritten. Existing-site adoption is deliberately refused.

`public/js/` uses native forms and dialogs. It does not replicate the legacy
150 KB custom matrix. The native child-table/dialog workflow is a development
interface; clinical usability parity has not been established.

Extension rule: add domain rules only with source evidence and regression tests.
Keep authorization in services, use request transactions, retain completed history,
and use actual site date/time utilities. Do not cache patient or permission results.
No speculative infusion, pharmacy distribution or mobile subsystem is included.

