# Performance assessment

The only measured workload is pure in-memory nursing-grid construction, recorded
in performance_results.json: 100 synthetic medication orders, 2,400 selectable
slots, 20 iterations. It excludes database, Frappe, permissions, network, UI and PDF.
Do not use it as an API, form-load or hospital-scale benchmark.

Source bottlenecks include 150 KB of monolithic form JavaScript and repeated CSS,
unbounded medication/practitioner lists, duplicate client-side saves, per-item
Medication reads, full schedule regeneration on every save, per-prescription
version writes, and overlapping discharge updates.

This alpha removes the legacy form bundle and duplicate client post-copy. Patient
API lists are paginated to 100 rows. Grid construction maps existing keys and
preserves history. Signature and discharge operations are serialized by admission.

Known remaining costs: version recalculation writes every prescription in an
admission; validation batches Medication policies in one read; server loads whole
prescriptions for administration; floor/doctor predicates need query plans. No
database indexes were added without representative plan measurements. No patient
or clinical permission cache is introduced.

Staging profiling must measure form/matrix load, schedule generation, duplication,
floor and doctor queries, discharge/reactivation and critical APIs at defined row
counts and concurrency. Record p50/p95, SQL counts, response sizes, lock contention,
query plans and history-preservation outcomes before choosing indexes/batching.

