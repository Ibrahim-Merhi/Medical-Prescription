# Configuration and site isolation

Medical Prescription Settings contains only organization name and logo, editable
by System Manager. Both print headers read it. This removes hospital branding
without adding configurable dosing or signature rules.

Original naming-series options are preserved for identifier continuity. Review
series configuration when adopting a site; do not reset an existing counter.

Frappe sites isolate data and configuration. There are no site names, server paths,
floor names, accounts, passwords or production record identifiers in app logic.

PINs must be reset by each nurse using the self-service button after staging
migration. Existing encrypted PINs are not accepted by the hash verifier. This is
an explicit security transition requiring nursing communication and cutover tests.

Clinical validation flags are server deployment attestations, not a UI setting
for bypassing clinical rules. Do not add a workflow flag merely to dismiss an
error. See validation_gates.md for evidence required before enabling any flag.

