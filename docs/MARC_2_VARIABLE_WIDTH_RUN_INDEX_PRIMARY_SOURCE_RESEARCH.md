# MARC2-VR16A Variable-Width Run-Index Primary-Source Research

Date: 2026-08-21

Lane: `MARC2-VR16A`

Status: **Artifact-only standards review; no private access or scientific
claim**

## Question

Does BIDS impose a one- or two-digit width on `run-<index>`, or should the
repair accept longer zero-padded numeric spellings while preserving the same
semantic run identity?

## Primary-Source Finding

BIDS 1.11.1 defines an `<index>` as a nonnegative integer that may be prefixed
with an arbitrary number of zeroes for consistent indentation. The run entity
is `run-<index>`, and the run appendix allows only nonnegative integers. The
entity table classifies `run` as numeric rather than alphanumeric.

Primary references, reverified 2026-08-21:

- [BIDS common principles](https://bids-standard.github.io/bids-specification-ignore/src/02-common-principles.html)
- [BIDS 1.11.1 run entity](https://bids-specification.readthedocs.io/en/stable/appendices/entities.html#run)
- [BIDS 1.11.1 entity table](https://bids-specification.readthedocs.io/en/stable/appendices/entity-table.html)

The engineering inference is narrow: `run-1`, `run-01`, `run-001`, and
`run-000001` may represent the same numeric index. This does not mean distinct
spellings can coexist safely in one logical companion set, and it does not
remove dataset-specific constraints on which semantic run indices are eligible.

## Repository Finding

VR12A intentionally froze `[0-9]{1,2}` and treated a three-digit run token as a
refusal witness. Consumed VR15P route `MARC2VR15P-R15` now shows that the real
target-free structural source falls in exactly that width class. No private
token or path was retained, so the repair must cover the entire standards-
allowed padding class instead of guessing one hidden width.

The next adapter should therefore:

1. accept one or more ASCII digits inside the existing 1,024-byte member-name
   cap;
2. canonicalize only for semantic grouping by stripping leading zeroes, with
   all-zero input canonicalized to `0`;
3. retain the existing dataset domain of semantic runs 1, 2, and 3;
4. preserve source-exact names and reservation bytes;
5. require all four companions for a logical run to use one identical lexical
   token;
6. refuse two different lexical spellings that normalize to the same logical
   companion; and
7. leave subject, session, task, suffix, entity-order, taxonomy, count, rank,
   split, storage, privacy, and scientific firewalls unchanged.

The full member-name cap supplies the resource bound; adding another arbitrary
run-width ceiling would repeat the standards mismatch. The adapter should not
parse a potentially long token into a large integer before confirming that its
canonical semantic value is one of the three frozen dataset runs.

## Claim Boundary

Engineering insight established: the one/two-digit restriction is narrower
than BIDS and is the exact aggregate structural class reached by VR15P.

Scientific claim not established: this standards review and aggregate route
contain no neural payload, target, model, prediction, score, neural effect, or
decoding result.
