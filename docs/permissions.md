# Permission architecture

Managers (System Manager, Healthcare Manager, Healthcare Administrator) have broad
row visibility, subject to native roles and User Permissions. Pharmacist, Resident
and Medical Prescription Viewer see prescriptions for active patients. Nurses
are restricted to today's active floor assignments. Doctors require an attending,
active Assigned Doctors, or active admission primary-practitioner relationship.
Unrecognized roles and Guest fail closed.

Multiple-role nursing users retain the floor restriction. This conservatively
combines the two active exported permission queries. Their original interaction
and nurse-manager combinations require validation with actual site role bundles.
The export uses `curdate()`; the new policy uses Frappe's site date.

List and direct-document prescription restrictions share one predicate. Patient
visibility is derived from the same policy. Native Frappe DocPerm/User Permissions
remain required; hooks return None when they do not deny an operation.

Generic prescription create/write belongs to doctor/manager roles. Nurses mutate
administration only through the role/floor checked API, with a narrowly scoped
child-row write. Read Only and Medical Prescription Viewer cannot prescribe.
Nurse PIN has no generic document permissions. No user is assigned a role by this
app. Existing roles are not overwritten.

The original Custom DocPerm grants are recorded for the eleven custom DocTypes
in doctype_inventory.json for comparison. They are not imported because broad
grants on standard Healthcare and unrelated ERP modules cannot be safely treated
as app requirements. Resident's intended edit privileges require site review.

Permission query SQL targets the original MariaDB table model. PostgreSQL
compatibility is not claimed. Tests with User Permissions, reports, exports,
REST, child access and mixed roles remain required on Frappe staging.

