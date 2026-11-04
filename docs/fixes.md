# Follow-up fixes and verification

- Prevent removing, re-keying or changing dose/route/frequency of an order with signed administration history. Stop remains possible while preserving original order context.
- Refresh dosage/signature policy on unstarted schedule slots; preserve signed slots verbatim.
- Prevent changing prescription dates after creation.
- Deny mutation APIs and second signatures for users with Read Only/Medical Prescription Viewer roles, even when another role grants nursing access.
- Reject blank signer logins before database lookup.
- Serialize floor-plan duplicate checks using an existing metadata-row lock; reject duplicate linked users and incomplete assignments.
- Batch medication policy reads instead of per-item queries.
- Paginate the print template over all medicines, retaining its original minimum two pages; use permission-aware first-prescription lookup and escape organization branding.
- Format Python and pass Ruff checks. Build wheel and source distribution successfully.

24 isolated/synthetic tests pass, including four signed-history/schedule regression cases, a mixed-role mutation denial, and three generic Jinja rendering cases. These are not Frappe integration tests.

Pending: dev-server connection and dependency inventory, actual installation, native Frappe permissions/concurrency, PDF visual QA, existing-site migration/adoption tooling, encounter conversion, PRN/overnight semantics, phone-order approvals, full nursing/pharmacy/Patient-Inpatient workflow parity and clinical signoff. Clinical write gates remain in place. GitHub authentication remains external to the app.
