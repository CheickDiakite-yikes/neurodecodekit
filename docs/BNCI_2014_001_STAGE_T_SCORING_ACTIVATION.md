# BNCI-C3C5-1 Stage T Scoring Activation

Date: 2026-08-25

Status: **Prepared with delayed effect. Target delivery and scoring remain
closed until this exact activation commit is pushed and both required CI jobs
pass.**

## Immutable Inputs

This activation binds:

- green Stage P/T implementation commit
  `7ba4f7c30f260bc7603e8928ad8d9ff010e54872`, CI `32906104408`;
- green prediction-freeze commit
  `2517fd16e7bf4cca077c46686320fe26c992ed69`, CI `32908059166`;
- the 5,037-byte freeze artifact at SHA-256
  `468fd77f45645620ff2636a3b00f587986d1ce0f73c4cad88896a8bd9b354057`;
  and
- all six unchanged implementation artifacts by byte count and SHA-256.

The activation changes no prediction, target, model, control, threshold, gate,
route, or private file.

## Enabled Operation

After this activation itself is remotely green, Stage T may execute once:

1. verify the committed freeze and all private prediction hashes;
2. verify the keyed Stage Q source-capability commitment;
3. verify the encrypted-target and scoring-key transport commitment;
4. write the permanent consumed marker;
5. open the scoring-key vault and decrypt exactly nine held-out-E target sets;
6. verify all 2,592 target identities against all 41,472 frozen condition rows;
7. apply the unchanged scorer and C3/C5-partial router once; and
8. emit only aggregate metrics and the registered route.

No parameter update, target-derived exclusion, calibration, selection, retry,
rerun, individual outcome publication, held-out-T delivery, or analysis network
access is enabled.

## Interpretation Ceiling

The maximum route is `BNCIC3C5-R5`. Even that route can establish only
participant-independent four-class BNCI protocol-condition prediction and
incremental scalp-EEG sensor information beyond the three recorded EOG
channels under this exact protocol.

It cannot establish thought or language decoding, executed movement intention,
exclusive motor-cortex origin, freedom from every peripheral or visual
confound, live decoding, portable hardware, home use, or clinical utility.
