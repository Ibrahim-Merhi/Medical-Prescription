# Troubleshooting

- Missing dependency: install the pinned prerequisite app on the staging site,
  not merely its source in the bench. Confirm Healthcare's app ID and Employee.
- Foreign-owned/custom DocType: follow migration.md. Do not force `custom=0`
  without a reviewed adoption plan and restore test.
- Field or Property Setter conflict: compare the reported definition to the
  source and target schema; merge explicitly. The installer does not overwrite.
- Print conflict: compare templates and approve a site-branding merge. Both
  original formats include a site-specific logo and fixed clinical stop text.
- Validation gate error: resolve the relevant blocker and run staging acceptance.
  Adding a flag is not a substitute for implementing or testing the workflow.
- PIN verification failure: reset the PIN using the nurse's own session; confirm
  enabled nurse role, distinct signer, floor access and rate-limit window. Never
  copy a PIN or hash into logs, issue trackers or support messages.
- Missing prescriptions: inspect native DocPerm/User Permissions, current active
  admissions, physician assignment and today's active floor plan. Test list and
  direct access with the same user.
- Unexpected course remaining days: compare selected-vs-all-grid-row completion
  with the legacy duplication rule before changing clinical logic.
- PDF mismatch: render synthetic records using the configured site renderer and
  print settings; verify logo access, page breaks, long comments and font glyphs.

