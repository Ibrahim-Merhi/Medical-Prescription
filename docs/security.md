# Security assessment and residual risks

Source weaknesses: permissions concentrated in list queries and UI buttons;
client-submitted signature state; separate PIN identity checks; password-based
second-signer LoginManager use; broad ignore_permissions; manual commits in
duplication; encrypted PIN comparison without rate limiting; raw destructive
maintenance APIs and HIS integration code mixed into the export.

Changes implemented: authenticated POST mutations; role and parent checks inside
services; shared list/direct row restrictions; native permissions retained;
server identities/timestamps; distinct second-nurse validation; PIN hashes with
PBKDF2-SHA256 (600,000 rounds, random 128-bit salt); constant-time digest comparison;
five attempts per session user per five-minute Redis window; no separate reusable
identity-proof response; no credential logging; no manual commit; history retention.

Escalations are narrow: self-owned PIN writes, configuration installation and
administration/discharge child/status writes after explicit authorization. They
require real Frappe security tests; code review alone does not prove safety.

Residual risks blocking release: floor-plan serialization under real concurrent DB transactions; incomplete emergency
audit policy; native User Permissions/report/REST behavior; doctor time-window
semantics; mixed-role precedence; read-only role interaction; completed-row update
guards; role grants on existing sites; replay/concurrent API behavior; distributed
throttle behavior and account-wide brute-force limits; credential reset rollout;
audit tamper resistance; print autoescape and PDF output; clinical workflow gaps.

The 6–12-digit PIN policy, second-nurse floor check, override reason and immutable
signed-history rules are deliberate security changes. They need nursing review
and migration communication; they are not represented as unchanged legacy behavior.

Configuration/source metadata only is included. No patient records, production
database dumps, credentials or raw source exports are bundled for GitHub.

