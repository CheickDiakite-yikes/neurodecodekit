# MARC2-VR35A Task-Aware Eligibility Repair Implementation

Date: 2026-08-23

Lane: `MARC2-VR35A`

Status: **Generated qualification passed; remote implementation proof pending**

Machine records:

- `registries/marc2_task_aware_eligibility_repair_implementation.v0.json`
- `registries/marc2_task_aware_eligibility_repair_result.v0.json`

## Proof Before Implementation

Exact registration `aa4c39a5ce8ca04627c9252600971ee878f20e3e` passed Base
Python job `97203738713`, Optional Neuro Readers job `97203738637`, and CI
`32643351246` before implementation began.

The registration binds eleven unchanged tracked artifacts totaling 250,900
bytes and contract SHA-256
`b801d9f1db51d7b6053f22bebd2d8dcda9e4987cbb242cf4f19b69f72fc46823`.

## Implemented Surface

The standard-library module
`src/neurodecodekit/datasets/marc2_task_aware_eligibility_repair.py` exposes
only:

- `plan`: inspect the fixed generated-only plan;
- `qualify`: run the one registered 20-path qualification.

There is no private `execute` or `inspect` command and no path, URL, output,
task, count, threshold, rank, cap, route, retry, or resource override.

The repair preserves task as a structural grouping dimension, verifies a
complete companion set independently for each task-bearing bundle, and then
projects exact lowercase ASCII `reachingandgrasping` bundles before applying
the unchanged VR2 participant/session classifier. Only an exact 195 projected
eligible bundles with the frozen participant-session distribution can reach
the unchanged rank-prefix, session split, and 8 GiB reservation selector.
Every selected source-exact name is then revalidated by the existing VR20A
selection firewall, which rejects any non-target task row.

## Measured Qualification

The sole qualification under one CPU thread, one worker, and one numerical job
passed all five cases in canonical and reversed order across two exact replays:

- four baseline `MARC2VR35A-G1` paths;
- four mixed-task-surplus `MARC2VR35A-G2` paths;
- four genuine target-task-surplus `MARC2VR35A-R1` paths;
- four genuine target-task-deficit `MARC2VR35A-R2` paths;
- four task/selection-firewall `MARC2VR35A-R3` paths.

The eight successful paths made eight selection calls and eight selection
validation calls. The mixed-task source produced the same semantic selected
cohort as the baseline after task projection, and all selected rows used the
exact published task. The pass also completed 99 direct refusals, 20 source
immutability checks, and exact deterministic replays.

It processed 8,836,768 generated input bytes in 1.2351410000119358 seconds at
36,044,800-byte peak RSS. The canonical aggregate report was 2,950 bytes and
retained output was zero. Raw-data reads, real-cache reads, model runs,
training runs, network calls, new payload bytes, private operations, and
cohort freezes were all zero.

## Interpretation And Boundary

VR35A demonstrates a real architectural defect class and a bounded repair on
generated fixtures: when eligibility omits task identity, an eligible bundle
from another task can inflate the count; exact-task projection removes that
surplus without changing the selected target-task cohort. It also proves that
true target-task surplus and deficit remain visible instead of being hidden by
the repair.

This does **not** establish that mixed-task surplus caused consumed private
route `MARC2VR34P-R2`. The private count, difference, task distribution,
identity, selection, and cohort remain unavailable, and no consumed private
lane was reopened. A real cohort freeze requires a separately frozen Tier C
packet and fresh decision after this implementation and its proof-only
closeout are remotely green.

Engineering capability added: generated MARC2 inventories can now preserve
task identity through structural validation and project the exact published
task before deterministic eligibility and selection.

Scientific claim not established: no real or private source, archive member,
neural signal, target, model, prediction, or score was accessed, so this
establishes no neural effect, decoding performance, language decoding,
unseen-person generalization, or live decoding capability.
