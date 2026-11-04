# Existing-site migration and rollback

Existing-site migration is **blocked pending a staged, reviewed ownership plan**.
This app intentionally does not flip `DocType.custom` automatically. Changing
module ownership and synchronizing metadata can have consequences outside SQL
table creation. No existing-site migration was executed.

Required process:

1. Back up site database, public/private files and configuration; test restore.
2. Restore to isolated staging with the original pinned app versions.
3. Run `medical_prescription.install.preflight`; capture all conflicts. This is
   read-only. Export metadata snapshots and child-table counts outside this repo.
4. Compare every existing field with `configuration/source_schema.json` and the
   app-managed definition, including mandatory/default/Link/child properties.
5. Reconcile missing schedule/order fields, duplicate medication keys, completed
   history and field-type conflicts. No automatic patient-data migration is supplied.
6. Review an explicit metadata adoption change set for the eleven DocTypes:
   module Medical Prescription and custom=0. Apply only in staging after verifying
   ownership, controller loading, field preservation and database backups. A
   production-approved adoption utility is still required; do not run raw SQL.
7. Compare Custom DocPerm with proposed role policy. Existing overrides can take
   precedence over exported permissions. Do not bulk-import the 414 exported rows.
8. Review old script deactivation by exact name, type, enabled state and script
   hash. Disable only replaced scripts after parity tests. No deactivation patch
   is supplied or executed. Keep unrelated HIS synchronization intact but inspect
   its interaction with Patient/Inpatient hooks.
9. Approve the two print header changes and merge template differences explicitly.
   Keep site branding in the singleton, not source files.
10. Install, migrate and build on staging; compare record names, row counts,
    prescription chains, all signatures and completed histories before and after.
11. Repeat migration and verify no additional mutations. Exercise all clinical
    acceptance scenarios before writing a production cutover plan.

Old Server APIs must not remain active with duplicate logic. In particular,
`Duplicate Prescription New` is the active duplicate API; `Duplicate Prescription`
is disabled and must stay disabled. Both active prescription permission scripts
must be replaced together. Disabled historical scheduler variants are not enabled.

Rollback: restore the complete backup into the original pinned application stack.
Do not uninstall/drop app-owned DocTypes on a live site as a rollback strategy.
Keep a metadata/script-state snapshot for diagnosis. No patient rows should be
deleted, renamed, or rewritten by an unreviewed migration.

