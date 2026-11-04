# Clean staging installation

This alpha has not been installed in a bench. Resolve the release gates first.
Use a disposable staging bench and synthetic records only.

1. Pin compatible Frappe, ERPNext and Healthcare v16 source versions. Use the
   Python/Node/database/Redis requirements documented by that exact Frappe release.
2. Download ERPNext and Healthcare source into the bench using their official
   repositories/branches. Confirm the Healthcare app ID is `healthcare`.
3. Install ERPNext on the staging site, then Healthcare and HRMS v16. Floor
   assignment links HRMS Employee and depends on its `user_id` field. These are
   administrator-run prerequisite steps, not automatic installs by this app.
4. Copy or clone this app into the bench. The following commands are templates,
   not executed deployment commands:

```sh
bench get-app /absolute/path/to/medical_prescription
bench --site STAGING_SITE execute medical_prescription.install.preflight
bench --site STAGING_SITE install-app medical_prescription
bench --site STAGING_SITE migrate
bench build --app medical_prescription
```

For a GitHub release, replace the local path with the authorized repository URL.
Do not execute placeholder commands literally. `required_apps` does not authorize
installing source or changing an existing server. This repository does not attempt
to install dependencies automatically.

Clean installation refuses foreign-owned/custom DocTypes bearing the same names.
All existing print/custom-field conflicts must be reconciled first. No schema or
patient data conversion happens in preflight. Never use this alpha to upgrade a
production site directly.

