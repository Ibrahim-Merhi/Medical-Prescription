# Missing components and inconsistent source definitions

Active scripts access fields absent from the exported definitions:

- Medical Prescription Item: `medication` (added as Data to match existing usage).
- Medication Administration Schedule: `medication`, `item_unique_key`,
  `reason_of_delay` (added, required by active script behavior).
- Past Drug Item: `ordered_by_practitioner`, `ordered_by_name`, `ordered_on`,
  `source_encounter` (added for history metadata used by active scripts).
- `dfg_estimates_mdrd` in duplicate source conflicts with actual
  `dfg_estimated_mdrd`; the actual defined identifier is used.

Other conflicts:

- `practitioner_name` is a Link to Healthcare Practitioner but encounter logic
  writes its human-readable name. The schema is retained; conversion is blocked.
- `prn` is Small Text, while scripts reduce it to 0/1. No automatic conversion.
- Item keys fall back to drug/medication, merging separate orders of the same drug.
  New items receive distinct stable keys; ambiguous historical keys require review.
- Before-save generates all 24 slots for every medicine, while the UI selects
  actual Step 1 times. Do not treat all grid rows as clinically ordered doses.
- Duplication decrements a course only when every non-disabled schedule row is
  complete. With 24 grid rows this may conflict with selected-dose intent; the
  exported rule is preserved in the pure implementation and requires review.
- Before-save stay duration and after-save/duplicate stay duration use different
  starting dates and inclusive counting. The controller uses the active after-save
  admission-based inclusive count; clinical acceptance remains required.
- Exported print layouts contain fixed automatic-stop text (heparin, steroids,
  narcotics, antibiotics and fluids). It is preserved as printed source content,
  not implemented as an automated medication-stopping rule.

Source schemas and source-file SHA-256 values are recorded for reproducibility.
No data migration has filled or rewritten patient/administration records.

