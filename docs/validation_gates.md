# Release blockers and clinical validation gates

The repository is a development alpha. These blockers prevent completion of the
master prompt's acceptance criteria and prevent a production-readiness claim.

1. **Runtime unavailable.** No Frappe/ERPNext/Healthcare, Redis, SQL site, browser
   or PDF renderer was available. Install/hook/API/permission behavior is untested.
2. **Encounter conversion conflict.** The active encounter Server Script writes
   no dose_number, dose_uom, frequency or route; the active before-save script
   requires all four. It also puts a practitioner display name into a Link and
   keys distinct orders by drug code. There is no safe verified transformation.
   Automatic encounter conversion is not installed.
3. **PRN mismatch.** `prn` is Small Text in schema but normalized as a boolean by
   active scripts. Preserve the schema and reconcile actual intent/history before
   implementing PRN administration.
4. **Overnight dates.** The grid spans 10:00 through 09:00, but all exported rows
   use the prescription date and Step 2 compares against the browser's current
   date. Agree the nursing-day/date mapping using real workflow evidence.
5. **Phone orders.** Browser JSON, approval identities and a separate phone grid
   lack a reliable server trust model. The legacy workflow is not replaced yet.
6. **Migration.** Custom DocType adoption, old script deactivation, Custom DocPerm
   precedence, duplicate keys, and patient-data preservation require staged tests.
7. **UI parity.** The native development forms replace the monolithic custom
   matrix, not its full clinical usability. Nursing/doctor/pharmacy review required.
8. **Discharge parity.** Native Healthcare discharge side effects, date clearing,
   pharmacy metadata, daily locks and treating-doctor behavior require reconciliation.
   The new service is gated and is not certified as parity-complete.
9. **Dependencies.** Confirm official v16 Python/Node versions, hook lifecycle,
   dependency app names, HRMS/Employee ownership and cache API from pinned source.
10. **Repository publication.** Confirm export/template redistribution rights,
    proposed MIT license, repository destination and release scope before pushing.

The server site config key `medical_prescription_validated_workflows` is an array
of validation attestations. Current gate names are `prescribing`, `duplication`,
`administration`, `overnight_dates`, `phone_orders`, and `discharge`. Default is
empty. A staging operator may enable a supported service only after its complete
functional/security/integration suite passes and the clinical owner signs off.
**No flag makes missing phone-order or PRN implementation complete.** Do not enable
`phone_orders` or `overnight_dates` before implementing the reconciled rules.

No method should be used for live medication administration in this alpha.

