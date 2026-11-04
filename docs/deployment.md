# GitHub, upgrades and controlled release

Repository: https://github.com/Ibrahim-Merhi/Medical-Prescription

This repository publishes an incomplete development alpha. No live ERPNext deployment is included.
Do not treat this alpha as a completed production release.

Before the first push: resolve validation_gates.md, review licensing and source
rights, choose the repository owner/name/visibility, verify no production exports
or secrets are tracked, run CI and staging acceptance, and review the final diff.
GitHub access is managed through the local Git credential configuration.

Recommended release progression: 0.1.0a1 local alpha; subsequent alpha tags for
staging work; 0.1.0 only after full functional/security/migration/PDF acceptance.
Tag stable releases and document supported pinned Frappe/ERPNext/Healthcare versions.
Do not imply major-version compatibility certifies every patch combination.

Upgrade process: back up and restore-test; pin apps; install on a cloned staging
site; run preflight; review metadata/fixture changes; migrate; build; exercise
clinical/regression suites; compare history/version counts; obtain cutover signoff.
Keep schema patches idempotent and non-destructive. No production upgrade patch
is supplied in this initial alpha.

Rollback uses a tested full site/files/configuration backup and original app
versions. Uninstalling app-owned clinical DocTypes is not a rollback procedure.

