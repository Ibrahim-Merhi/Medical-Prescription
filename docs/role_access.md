# Role access

App-owned DocTypes use native DocPerm entries. System Manager and Healthcare Administrator
can read/create/edit prescriptions, floors, service units and floor assignment plans.
Doctors, Physicians, Healthcare Practitioners and Healthcare Users can read/create/edit
prescriptions and read floor/unit/assignment masters. Nurses, Nursing Users, Nurse Supervisors,
Nursing Managers, Pharmacists, Residents and Medical Prescription Viewers can read prescriptions
and those masters. Nursing supervisors/managers can also create/edit assignment plans.
Clinical roles receive print/report access; delete remains disabled. Census reports include
clinical managers and nursing supervisors/managers.

Existing prescription/patient row restrictions still apply. Nursing supervisors/managers
follow assigned-floor scope. Read-only roles still block ordinary users from writes;
Administrator is exempt. Nursing/pharmacy clinical actions use their dedicated endpoints,
not general prescription editing. Settings remain restricted to System Manager; Nurse PIN
storage has no list permission. Child tables inherit access through parent records.

ERPNext, Healthcare and HRMS DocTypes (Patient, Inpatient Record, Employee, Medication,
Healthcare Practitioner, Item, etc.) retain their native permissions. Grant those through
Role Permission Manager as appropriate. No shared native permission table is replaced.

Migration synchronizes standard app permissions. Existing Custom DocPerm overrides may
continue to take precedence. To apply the shipped defaults to an app-owned DocType with
custom overrides, back up/review the overrides then use Reset in Role Permission Manager
for that specific DocType. This intentionally requires an explicit administrator choice.

Local policy and metadata tests do not replace real-site role acceptance. Verify a doctor,
assigned nurse, pharmacist and restricted viewer after migrating the development site.
