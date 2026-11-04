# Medical Prescription

Frappe application title: **Medical Prescription**. Package, Bench app ID and proposed
repository name: `medical_prescription`. Version: `0.1.0a1`.

This is a local development alpha reconstructed from eight configuration exports.
It is **not a completed migration, production release, or verified installable build**.
No server was modified. GitHub publication of this alpha does not constitute a production release.

Included: 11 source-derived custom DocTypes, one print-branding settings DocType,
35 scoped Custom Fields, two parameterized print templates, native forms,
permission policies, prescription/version services, duplicate-course logic,
administration actions, PIN hashing, discharge/reactivation services, conflict
preflight, isolated tests, and CI configuration.

The original monolithic Client/Server Scripts are not installed as fixtures.
Unrelated HR, payroll, accounting, HIS import and destructive maintenance code
are excluded. Existing roles and standard Healthcare DocTypes are not replaced.

Clinical writes are gated pending staging validation. Encounter conversion,
phone-order approval, PRN reconciliation and existing-site metadata adoption
remain blocked; these are not implemented replacements for those legacy workflows.
See [validation gates](docs/validation_gates.md) and [functionality matrix](docs/functionality.md).

Read [installation](docs/installation.md), [migration](docs/migration.md),
[security](docs/security.md) and [test report](docs/testing.md) before staging use.
The supplied prompt's final acceptance criteria are **not yet met**.

Run local isolated checks from this directory:

```sh
python3 -m unittest discover -s tests -v
```

MIT license is proposed for the new repository. Confirm rights to redistribute
the supplied configuration and print layouts before publishing.

