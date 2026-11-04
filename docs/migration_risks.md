# Migration risk assessment

|Risk|Impact|Control/status|
|---|---|---|
|Database-managed DocType adoption|Metadata overwrite/controller change|Installer refuses; reviewed staging adoption utility pending|
|Schema fields missing in export|Lost medication identity/signatures|Add source-evidenced fields; reconcile historical rows before conversion|
|Duplicate drug-derived keys|Two medication orders share schedule state|New distinct keys; ambiguous legacy rows fail closed|
|Custom DocPerm precedence|Unintended grants/restrictions|60 scoped rows inventoried for review, not imported|
|Property Setters|Standard/custom field behavior differs|68 scoped setters inventoried; conflicting field policies rejected|
|Two active permission queries|Mixed role behavior uncertain|Conservative combined nursing policy; staged role regression pending|
|Duplicate scripts remain active|Double writes/order-dependent behavior|No automatic migration; exact-name/hash cutover still required|
|Native Healthcare side effects|Admission/discharge inconsistency|Explicit service gated; pinned controller review pending|
|PIN hash transition|Nurses unable to cosign after cutover|Self-reset workflow and nursing communication required|
|Fixed print content/assets|Wrong branding or clinical instructions|Branding parameterized; clinical text retained and requires review|
|Incomplete UI/workflow parity|Clinical work blocked or changed|Alpha only; not a production cutover candidate|

