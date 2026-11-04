# Existing functionality and implementation matrix

“Implemented, unintegrated” means code exists but has not run in Frappe. It does
not mean the clinical workflow has passed acceptance tests.

|Legacy behavior|Destination/status|
|---|---|
|Eleven custom DocTypes and child relationships|App JSON definitions; static linkage checked|
|Create/edit prescription|Controller + prescription service; implemented, unintegrated; gated|
|Daily duplicate and remaining courses|Duplication service + pure domain rules; isolated rules tested; gated|
|Version sequence/latest flag|Admission-serialized on_update; implemented, unintegrated|
|Nursing 10:00–09:00 matrix|24 selectable slots preserved; native development dialog; full matrix UX pending|
|Frequency minimum spacing|Pure rule tested across midnight; administration integration pending|
|Step 1 cutoff and emergency roles|Server service; reason added; implemented, unintegrated|
|Step 2 timing/delay reason|Server service; implemented, unintegrated; overnight date mapping blocked|
|Two nurse signatures|PIN checked inside administration write; one-way hash tested; runtime pending|
|PIN self-service|Dedicated endpoint and User button; reset transition required|
|Completed administration protection|Grid retention and save guard; isolated grid tests passed; direct REST tests pending|
|Hold and Stop|Administration denied; stopped schedule creation skipped; history retained; runtime pending|
|PRN|Schema preserved; administration blocked pending text/boolean reconciliation|
|Phone orders and approvals|Not migrated; ambiguous approval trust model; prescribing gate refuses by default|
|Floor assignment validation|Controller; duplicate nurse/user checks; concurrency uniqueness still pending|
|Doctor/nurse/viewer restrictions|Shared list/direct policy; isolated predicates tested; runtime pending|
|Patient admission history and creation actions|Patient navigation exists; full admission UI/synchronization pending|
|Attending/treating doctor rules|One active treating doctor + duplicate-assignment validation; full synchronization pending|
|Encounter-to-prescription|Blocked by incompatible active script requirements; not installed|
|Discharge without prescription|Service accepts zero linked prescriptions; implemented, unintegrated; gated|
|Reactivation|Service rejects competing active admission, reopens latest and preserves completed rows; parity incomplete|
|Pharmacy clearance and medication-sent UX|Fields preserved; full workflow pending|
|Two print formats|HTML/layout retained except site branding; Jinja/PDF render not yet validated|
|Existing-site conversion|Preflight implemented; metadata adoption and script-deactivation tooling pending|
|Unrelated HIS/HR/payroll/ERP customizations|Excluded from installation|

