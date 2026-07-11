# Security And Sensitive-Data Reporting

## Supported Versions

NeuroDecodeKit is pre-1.0 research software. Security fixes target the current
default branch and the latest tagged `0.1.x` release when one exists. Older
commits and research artifacts may not receive backports.

## Report Privately

Do **not** open a public issue for:

- exposed credentials, signed URLs, or device/cloud tokens;
- a path escape, unsafe symlink, arbitrary file read/write, or archive issue;
- malicious pickle/object loading or unsafe deserialization;
- a download guard that can exceed its declared file or byte cap;
- accidental access to event/target/participant content;
- raw or derived neural data committed to Git or attached to an issue;
- an artifact that leaks absolute paths, participant metadata, free text,
  device identifiers, or exact acquisition timestamps;
- a way to bypass split, holdout, provenance, or tamper validation when that
  could create a false scientific claim.

Use GitHub's private vulnerability-reporting or security-advisory flow:

https://github.com/CheickDiakite-yikes/neurodecodekit/security/advisories/new

If that route is unavailable, contact the lead maintainer through
https://github.com/CheickDiakite-yikes and request a private channel. Do not
include a secret, participant detail, recording link, or exploit in a public
message.

## What To Include

Provide only the minimum information needed to reproduce the issue:

- affected command, module, schema, and commit;
- operating system and Python version;
- installed optional extras and package versions;
- expected boundary and observed behavior;
- a synthetic or redacted reproduction when possible;
- impact, prerequisites, and whether any real data or credentials were exposed;
- suggested mitigation, if known.

Do not attach a real recording. If the problem appears only with private data,
describe the file family and structural condition, then help construct a
synthetic reproducer.

## Response And Disclosure

Maintainers will review reports on a best-effort basis, confirm the safe next
step when possible, and coordinate disclosure after a fix or containment plan
exists. No fixed response-time guarantee is offered by this volunteer research
project.

If a real credential was exposed, revoke or rotate it immediately; deleting a
file or commit is not sufficient. If participant data was exposed, stop further
distribution and follow the dataset steward's, institution's, consent, and
applicable legal incident procedures.

## Security Boundaries

NeuroDecodeKit reduces risk through local-first operation, optional heavy
dependencies, strict schemas, relative-path reports, bounded reads/writes,
hashes, collision refusal, dry-run downloads, and synthetic-first validation.
These controls do not make neural data anonymous or make the software suitable
for clinical or safety-critical use.

Never run untrusted recording files, model checkpoints, NumPy object arrays,
pickle files, archives, notebooks, or vendor SDK binaries merely because they
were linked from an issue.
