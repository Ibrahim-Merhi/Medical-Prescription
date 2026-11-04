# Duplicate-code and authority assessment

The enabled `Duplicate Prescription New` is authoritative over disabled
`Duplicate Prescription`. Disabled scheduler/encounter variants remain disabled.
Active `Medical Prescription Full` (before save), `Medical Presc` (after save) and
`Patient Encounter` (after submit) interact and have incompatible field assumptions;
enabled state alone does not establish a safe execution order or behavior.

Two active Medical Prescription permission queries (`MEd` and `Floor permision`)
overlap. The new policy combines active-patient/doctor scope with the nursing
floor restriction. Mixed manager/nurse precedence still needs site validation.

The large Medical Prescription Client Script defines
`sync_doctor_medications_after_duplicate` twice. It can save copied data after the
server duplicate response, conflicting with server course/stopping decisions.
The new frontend calls a single server duplicate endpoint and does not perform a
second client-side medication copy.

The original before-save schedule state loads old persisted signatures, then
overwrites them with client-supplied state. The new normal-save guard rejects
administration changes; the nursing service stamps identities server-side.

Parallel Patient/Inpatient/prescription discharge handlers use direct writes,
making order and multiple-active-admission behavior uncertain. This alpha does
not install those overlapping scripts; the explicit transition service is gated.

