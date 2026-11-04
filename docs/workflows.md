# Prescription, nursing, doctor and discharge workflows

Prescription: an authorized doctor creates an admission-linked prescription. The
server checks patient/admission consistency, site access, required medication
fields, distinct order keys and medication signature policy. It generates the
24-slot nursing grid and recalculates chronological versions under an admission
lock. Latest-version and one-hour editing restrictions are enforced in the
controller; exact legacy emergency semantics still need validation.

Duplicate: authorized callers choose a later date. Repeated source/date requests
return the prior result after permission checks. Stopped/one-time/completed
medicines move to history; pending phone orders are omitted according to source
behavior. Existing completed administrations stay with the original prescription.

Nursing: read access and current floor assignment are required. Step 1 validates
a slot under the exported frequency-spacing rule and 10:00 cutoff. Emergency
roles require a reason. Step 2 requires locked Step 1, a reason outside ±1 hour,
and a distinct authorized PIN signer when required. User IDs and site timestamps
are stored on the server. PRN, phone and unresolved overnight behavior are blocked.

Doctor assignments: Patient validation rejects more than one active Treating
doctor and duplicate practitioner/admission/role tuples. Full primary-practitioner
synchronization from admissions is not implemented in this alpha.

Discharge/reactivation: dedicated roles and a reason are required. Patient and
admission locks protect cross-document updates. Discharge accepts admissions
without prescriptions. Reactivation rejects another active admission, sets the
admission to Admission Scheduled, reopens only the latest prescription, and leaves
completed administration rows intact. Full native Healthcare side effects,
clearance stamps, discharge date handling and inpatient hook parity remain pending.

