# Test report

Executed locally on 2026-11-04:

|Check|Result|Limit|
|---|---|---|
|UTF-8 CSV parsing and row-width validation|8 files passed; zero malformed rows|Metadata/configuration only|
|Isolated Python suite|16 tests passed, zero failures|Python 3.9.6, not target Python 3.14/Frappe|
|Python AST parsing|Passed for all repository Python files|No Frappe imports/runtime exercised|
|App child-table linkage and field identity|Passed for 12 DocTypes|No database schema synchronization|
|JavaScript syntax|All 3 form scripts passed Node --check|No browser/Frappe UI exercised|
|Pure grid microbenchmark|Executed; see performance_results.json|No API/SQL/browser measurement|
|Jinja/PDF render|Not executed|Renderer and Jinja unavailable locally|
|Wheel/sdist build|Not executed|Build dependencies unavailable; download timed out|
|Ruff lint|Not executed locally|Ruff unavailable; dependency download timed out|
|CI workflow|Configured, not executed on GitHub|Execution not verified in GitHub Actions|

The suite covers distinct orders for the same medicine, stable 24-slot generation,
idempotent rebuild, completed/removed-order history retention, ambiguous-key
rejection, stopped/pending-phone slot exclusion, hold-grid retention, overnight
spacing, period parsing, duplicate-course outcomes, isolated role predicates,
metadata structure, no guest mutation decorators/manual commits, print-branding
parameterization, and salted PIN hashing/verification.

Tests under tests/test_permissions.py use a fake Frappe object. They test predicate
construction, not actual SQL permissions. PIN tests exercise hashing, not Redis or
Frappe credential access. Do not report them as integration/security certification.

## Required staging acceptance (all not executed)

|Scenario group|Required checks|
|---|---|
|Prescription creation/editing|Required fields, patient/admission scope, time lock, versions and latest flags|
|Duplication|Course/one-time/stopped behavior, repeat request, concurrent requests, source permissions|
|Scheduling|Intervals, custom times, date boundaries, overnight nursing day, preservation|
|Administration|Step 1/2 ordering, server timestamps, duplicate actions and concurrent nurses|
|Double signature/PIN|Distinct enabled nurse, floor permission, invalid PIN, throttle, reset, no plaintext responses|
|PRN/Hold/Stop|Reconciled PRN behavior, denial while held/stopped, completed history immutable|
|Phone orders|Nurse entry, doctor approval, signature provenance and replay protection after implementation|
|Floor/doctor access|Today's plan, shift policy, duplicate plans, treating/consultant/attending, mixed roles|
|Resident/read-only roles|Native create/write/read/print/report/REST permissions, role combinations|
|Emergency override|Authorized roles, required reason, audit history, no signature bypass|
|Patient/Inpatient|Active admission selection, practitioner synchronization, no duplicate doctors|
|Discharge/reactivation|With/without prescription, native Healthcare side effects, competing active admission, rollback on failure|
|Print formats|Jinja synthetic records, empty/long orders, comments, font glyphs, multipage PDF and branding|
|Migration|Clean install, reviewed existing-site adoption, repeat migration, conflicts, old script deactivation and restore|
|Performance|Form/matrix/API latency, SQL counts, query plans, concurrency and lock contention|

Use synthetic records in an isolated site matching the pinned dependency versions.
Capture expected outcomes from the verified source/site before enabling a gate.
Measure performance against a stated workload. Clinical reviewers must approve
medication, signature, discharge and nursing-day semantics. A successful install
alone does not satisfy these tests.

