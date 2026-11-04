# Dependency and compatibility matrix

|Component|Why required|Status|
|---|---|---|
|Frappe v16|Document model, sessions, permissions, hooks, transactions|Not installed locally|
|ERPNext v16|Item, UOM, Employee and common ERP dependencies|Not installed locally|
|Healthcare v16|Patient, Inpatient Record, Medication, Encounter, Practitioner|Mandatory; not installed locally|
|HRMS v16|Floor Assignment Detail links Employee and derives the nurse User|Declared prerequisite to preserve the exported employee-based floor model; runtime untested|
|Redis|PIN verification throttling through site cache|Runtime test required|
|PDF renderer|Both exported formats identify their renderer in configuration JSON|Runtime render test required|

The supplied source environment reports Frappe 16.17.5, ERPNext 16.17.0,
Healthcare 16.0.8 and HRMS 16.6.1. These are source provenance, **not tested
compatibility claims**. No patch combination is certified by this repository.

`required_apps` declares prerequisites and the install hook requires their site
installation. It does not replace administrator control of source download,
site installation, migrations or assets. Downloading an app into a bench is
different from installing it on a site. Major-version checks reject other majors;
they cannot prove compatibility with all v16 patch releases.

Official references to verify against pinned target versions:

- https://docs.frappe.io/framework/user/en/python-api/hooks
- https://github.com/frappe/frappe/tree/version-16
- https://github.com/frappe/erpnext/tree/version-16
- Healthcare source repository and branch used by the target installation

Official version-16 source was retrieved during local review. Frappe's
[pyproject.toml](https://github.com/frappe/frappe/blob/version-16/pyproject.toml)
requires Python >=3.14,<3.15; this app declares the same range. The local isolated
test interpreter is older and therefore does not validate the target runtime.
Healthcare's [hooks.py](https://github.com/frappe/health/blob/version-16/healthcare/hooks.py)
confirms app ID `healthcare` and `required_apps = ["frappe/erpnext"]`.
Additional hook/cache/installation and Healthcare transition verification remains
required against pinned release commits; network access was intermittent.

