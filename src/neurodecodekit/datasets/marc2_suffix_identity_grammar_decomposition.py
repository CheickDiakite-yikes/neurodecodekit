"""Generated-only decomposition of MARC2 suffix-bearing identity grammar."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import os
import re
import resource
import sys
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_p15_run_index_repair as vr12a

SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR15A"
CONTRACT_SCHEMA_NAME = "neurodecodekit.marc2_suffix_identity_grammar_decomposition_contract"
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_suffix_identity_grammar_decomposition_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_suffix_identity_grammar_decomposition_contract.v0.json"
)
CONTRACT_SHA256 = "10644f5487069c3143a55f1910d07f7e7572bcd6ed21fdc2620a8a649b26a058"
CONTRACT_BYTES = 9_287
GREEN_REGISTRATION_COMMIT = "185fbc54366fd0eaf0ed4e994511e4485514b53e"
GREEN_REGISTRATION_CI_RUN_ID = 32_447_836_662
GREEN_REGISTRATION_BASE_JOB_ID = 96_670_618_009
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 96_670_617_843
SUCCESS_ROUTE = "MARC2VR15A-G1"
RESULT_ROUTES = tuple(f"MARC2VR15A-R{index}" for index in range(1, 17))
REFUSAL_ROUTES = tuple(f"MARC2VR15A-F{index:02d}" for index in range(1, 7))
CASES = (
    "control_success",
    "tail_component_count",
    "prefix_segment_grammar",
    "subject_directory_shape",
    "session_directory_shape",
    "modality_directory",
    "filename_subject_shape",
    "filename_subject_disagreement",
    "filename_session_shape",
    "filename_session_disagreement",
    "task_entity_shape",
    "optional_entity_shape",
    "run_entity_absent",
    "run_entity_not_terminal",
    "run_token_nonnumeric",
    "run_token_width",
    "multiple_identity_classes",
)
ORDERS = ("canonical", "reversed")
REPLAYS = 2
CASE_ROUTES = dict(zip(CASES, (SUCCESS_ROUTE, *RESULT_ROUTES), strict=True))
SINGLE_CLASS_CASES = CASES[1:-1]
EXPECTED_P15 = (
    "MARC2VR12A-F03",
    "P15 suffix-bearing BIDS identity differs",
)
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
PREFIX_RE = re.compile(r"[A-Za-z0-9._-]+\Z")
SUBJECT_RE = re.compile(r"sub-[0-9]{2}\Z")
SESSION_RE = re.compile(r"ses-[0-9]{2}\Z")
TASK_RE = re.compile(r"task-[A-Za-z0-9]+\Z")
OPTIONAL_RE = re.compile(r"[A-Za-z0-9]+-[A-Za-z0-9]+\Z")
ASCII_DIGITS_RE = re.compile(r"[0-9]+\Z")
EXPECTED_REPAIRED_PATTERN = (
    r"(?:[A-Za-z0-9._-]+/)*"
    r"(?P<subject>sub-[0-9]{2})/(?P<session>ses-[0-9]{2})/eeg/"
    r"(?P=subject)_(?P=session)_task-(?P<task>[A-Za-z0-9]+)"
    r"(?:_[A-Za-z0-9]+-[A-Za-z0-9]+)*_run-(?P<run>[0-9]{1,2})"
    r"(?P<suffix>_eeg\.eeg|_eeg\.vhdr|_eeg\.vmrk|_events\.tsv)\Z"
)
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "candidate",
        "cohort",
        "entries",
        "event",
        "failed_value",
        "label",
        "labels",
        "member_name",
        "participant_id",
        "path",
        "prediction",
        "predictions",
        "private_manifest",
        "reason",
        "row",
        "row_index",
        "run_id",
        "safe_reason",
        "selection",
        "session_id",
        "signal",
        "source_identity",
        "subject_id",
        "suffix",
        "target",
        "targets",
    }
)


class SuffixIdentityGrammarRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR15A refusal route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR15A refusal route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


@dataclass(frozen=True, slots=True)
class GrammarDecision:
    """One aggregate generated route without source identity or detail."""

    route: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                allow_nan=False,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError) as exc:
        raise SuffixIdentityGrammarRefusal(
            REFUSAL_ROUTES[3], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON constant")


def _strict_json(payload: bytes) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("utf-8", "strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
        raise SuffixIdentityGrammarRefusal(
            REFUSAL_ROUTES[0], "registered JSON is unavailable"
        ) from exc
    if not isinstance(value, dict):
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[0], "registered JSON shape differs")
    return value


def _read_fixed(root: Path, relative: str) -> bytes:
    path = root / relative
    try:
        if path.is_symlink() or not path.is_file():
            raise OSError("fixed artifact is not a regular file")
        path.resolve(strict=True).relative_to(root.resolve(strict=True))
        return path.read_bytes()
    except (OSError, ValueError) as exc:
        raise SuffixIdentityGrammarRefusal(
            REFUSAL_ROUTES[1], "fixed artifact is unavailable"
        ) from exc


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR15A contract."""

    payload = _read_fixed(root or _repo_root(), str(CONTRACT_RELATIVE_PATH))
    if len(payload) != CONTRACT_BYTES or _sha256_bytes(payload) != CONTRACT_SHA256:
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[0], "registered contract hash differs")
    return _strict_json(payload)


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    registered = load_registered_contract()
    if (
        not isinstance(contract, dict)
        or contract != registered
        or contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status") != "preregistered_artifact_only_generated_only_no_private_access"
    ):
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[0], "registered contract mapping differs")


def _verify_registration_proof(
    *,
    commit: str = GREEN_REGISTRATION_COMMIT,
    ci_run_id: int = GREEN_REGISTRATION_CI_RUN_ID,
    base_job_id: int = GREEN_REGISTRATION_BASE_JOB_ID,
    optional_job_id: int = GREEN_REGISTRATION_OPTIONAL_JOB_ID,
) -> None:
    if (
        commit != "185fbc54366fd0eaf0ed4e994511e4485514b53e"
        or ci_run_id != 32_447_836_662
        or base_job_id != 96_670_618_009
        or optional_job_id != 96_670_617_843
    ):
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[0], "registration proof differs")


def _fixed_payloads(contract: Mapping[str, Any], root: Path | None = None) -> dict[str, bytes]:
    repo = root or _repo_root()
    return {row["path"]: _read_fixed(repo, row["path"]) for row in contract["fixed_inputs"]}


def _verify_fixed_payloads(contract: Mapping[str, Any], payloads: Mapping[str, bytes]) -> int:
    rows = contract.get("fixed_inputs")
    if not isinstance(rows, list) or len(rows) != 11:
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[1], "fixed artifact inventory differs")
    expected_paths = {row.get("path") for row in rows if isinstance(row, dict)}
    if set(payloads) != expected_paths:
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[1], "fixed artifact set differs")
    total = 0
    for row in rows:
        path = row.get("path")
        payload = payloads.get(path)
        if (
            not isinstance(path, str)
            or not isinstance(payload, bytes)
            or len(payload) != row.get("bytes")
            or _sha256_bytes(payload) != row.get("sha256")
        ):
            raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[1], "fixed artifact identity differs")
        total += len(payload)
    if total != contract.get("fixed_input_bytes"):
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[1], "fixed artifact byte total differs")
    return total


def _static_pattern_from_ast(module_payload: bytes) -> str:
    try:
        tree = ast.parse(module_payload.decode("utf-8", "strict"))
    except (SyntaxError, UnicodeDecodeError) as exc:
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[1], "VR12A AST is unavailable") from exc
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "REPAIRED_CORE_MEMBER_RE"
            for target in node.targets
        ):
            continue
        if (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and isinstance(node.value.func.value, ast.Name)
            and node.value.func.value.id == "re"
            and node.value.func.attr == "compile"
            and node.value.args
            and isinstance(node.value.args[0], ast.Constant)
            and isinstance(node.value.args[0].value, str)
        ):
            return node.value.args[0].value
    raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[1], "VR12A repaired regex is unavailable")


def _static_p15_guard_count(module_payload: bytes) -> int:
    try:
        tree = ast.parse(module_payload.decode("utf-8", "strict"))
    except (SyntaxError, UnicodeDecodeError) as exc:
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[1], "VR12A AST is unavailable") from exc
    count = 0
    for function in (
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_validate_repaired_entry"
    ):
        for node in ast.walk(function):
            if not isinstance(node, ast.Raise) or not isinstance(node.exc, ast.Call):
                continue
            call = node.exc
            if (
                isinstance(call.func, ast.Name)
                and call.func.id == "P15RunIndexRepairRefusal"
                and len(call.args) >= 2
                and isinstance(call.args[0], ast.Subscript)
                and isinstance(call.args[0].value, ast.Name)
                and call.args[0].value.id == "REFUSAL_ROUTES"
                and isinstance(call.args[0].slice, ast.Constant)
                and call.args[0].slice.value == 2
                and isinstance(call.args[1], ast.Constant)
                and call.args[1].value == EXPECTED_P15[1]
            ):
                count += 1
    return count


def _verify_static_grammar(contract: Mapping[str, Any], payloads: Mapping[str, bytes]) -> int:
    path = "src/neurodecodekit/datasets/marc2_p15_run_index_repair.py"
    module_payload = payloads.get(path)
    basis = contract.get("grammar_basis")
    if not isinstance(module_payload, bytes) or not isinstance(basis, dict):
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[1], "static grammar input differs")
    if (
        _static_pattern_from_ast(module_payload) != EXPECTED_REPAIRED_PATTERN
        or vr12a.REPAIRED_CORE_MEMBER_RE.pattern != EXPECTED_REPAIRED_PATTERN
        or tuple(vr12a.selector.REQUIRED_SUFFIXES)
        != ("_eeg.eeg", "_eeg.vhdr", "_eeg.vmrk", "_events.tsv")
        or basis.get("exact_P15_route") != EXPECTED_P15[0]
        or basis.get("exact_P15_reason") != EXPECTED_P15[1]
        or _static_p15_guard_count(module_payload) != 1
    ):
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[1], "static grammar binding differs")
    return 1


def _strip_required_suffix(name: str) -> str:
    matches = [value for value in vr12a.selector.REQUIRED_SUFFIXES if name.endswith(value)]
    if len(matches) != 1:
        raise SuffixIdentityGrammarRefusal(
            REFUSAL_ROUTES[2], "generated P15 witness suffix differs"
        )
    return name[: -len(matches[0])]


def _classify_identity_name(name: str) -> str:
    """Classify one generated P15 name using the frozen ordered grammar."""

    try:
        normalized = vr12a.selector._normalize_member_name(name)
    except vr12a.selector.FreewillPrefixSelectionRefusal as exc:
        raise SuffixIdentityGrammarRefusal(
            REFUSAL_ROUTES[2], "generated P15 witness is not normalized"
        ) from exc
    if normalized != name or vr12a._repaired_core_match(name) is not None:
        raise SuffixIdentityGrammarRefusal(
            REFUSAL_ROUTES[2], "generated P15 witness is not classifiable"
        )
    stem = _strip_required_suffix(name)
    parts = stem.split("/")
    if len(parts) < 4:
        return RESULT_ROUTES[0]
    prefix, tail = parts[:-4], parts[-4:]
    if any(PREFIX_RE.fullmatch(value) is None for value in prefix):
        return RESULT_ROUTES[1]
    directory_subject, directory_session, modality, filename = tail
    if SUBJECT_RE.fullmatch(directory_subject) is None:
        return RESULT_ROUTES[2]
    if SESSION_RE.fullmatch(directory_session) is None:
        return RESULT_ROUTES[3]
    if modality != "eeg":
        return RESULT_ROUTES[4]
    tokens = filename.split("_")
    if not tokens or SUBJECT_RE.fullmatch(tokens[0]) is None:
        return RESULT_ROUTES[5]
    if tokens[0] != directory_subject:
        return RESULT_ROUTES[6]
    if len(tokens) < 2 or SESSION_RE.fullmatch(tokens[1]) is None:
        return RESULT_ROUTES[7]
    if tokens[1] != directory_session:
        return RESULT_ROUTES[8]
    if len(tokens) < 3 or TASK_RE.fullmatch(tokens[2]) is None:
        return RESULT_ROUTES[9]
    remaining = tokens[3:]
    run_positions = [index for index, token in enumerate(remaining) if token.startswith("run-")]
    if not run_positions:
        return RESULT_ROUTES[11]
    if run_positions[-1] != len(remaining) - 1:
        return RESULT_ROUTES[12]
    if any(OPTIONAL_RE.fullmatch(token) is None for token in remaining[:-1]):
        return RESULT_ROUTES[10]
    value = remaining[-1][len("run-") :]
    if not value or ASCII_DIGITS_RE.fullmatch(value) is None:
        return RESULT_ROUTES[13]
    if len(value) not in (1, 2):
        return RESULT_ROUTES[14]
    raise SuffixIdentityGrammarRefusal(
        REFUSAL_ROUTES[2], "generated P15 witness has no grammar class"
    )


def _replace_once(name: str, old: str, new: str) -> str:
    if name.count(old) != 1:
        raise SuffixIdentityGrammarRefusal(
            REFUSAL_ROUTES[2], "generated witness construction refused"
        )
    return name.replace(old, new, 1)


def _mutate_name(name: str, case: str) -> str:
    match = vr12a._repaired_core_match(name)
    if match is None:
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[2], "generated witness source differs")
    subject = match.group("subject")
    session = match.group("session")
    if case == "tail_component_count":
        return name.rsplit("/", 1)[-1]
    if case == "prefix_segment_grammar":
        return _replace_once(name, "Freewill_generated/", "Freewill generated/")
    if case == "subject_directory_shape":
        return _replace_once(name, f"/{subject}/", "/participant-01/")
    if case == "session_directory_shape":
        return _replace_once(name, f"/{session}/", "/visit-01/")
    if case == "modality_directory":
        return _replace_once(name, "/eeg/", "/meg/")
    if case == "filename_subject_shape":
        return _replace_once(name, f"/{subject}_", "/participant-01_")
    if case == "filename_subject_disagreement":
        return _replace_once(name, f"/{subject}_", "/sub-99_")
    if case == "filename_session_shape":
        return _replace_once(name, f"_{session}_", "_visit-01_")
    if case == "filename_session_disagreement":
        return _replace_once(name, f"_{session}_", "_ses-99_")
    if case == "task_entity_shape":
        return _replace_once(name, "task-freewill", "task-free.will")
    if case == "optional_entity_shape":
        return _replace_once(name, "_run-", "_acq-hi-res_run-")
    if case == "run_entity_absent":
        return re.sub(r"_run-[0-9]{1,2}(?=_)", "", name, count=1)
    if case == "run_entity_not_terminal":
        return re.sub(r"_run-([0-9]{1,2})(?=_)", r"_run-\1_acq-copy", name, count=1)
    if case == "run_token_nonnumeric":
        return re.sub(r"_run-[0-9]{1,2}(?=_)", "_run-x", name, count=1)
    if case == "run_token_width":
        return re.sub(r"_run-[0-9]{1,2}(?=_)", "_run-001", name, count=1)
    raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[2], "generated case differs")


def _build_case(case: str, order: str) -> dict[str, Any]:
    if case not in CASES:
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[2], "generated case differs")
    try:
        source = vr12a.build_generated_variant("padded_control", order)
        if case == "control_success":
            return source
        changed = copy.deepcopy(source)
        targets = [
            row
            for row in changed["entries"]
            if isinstance(row, dict)
            and isinstance(row.get("member_name"), str)
            and vr12a._repaired_core_match(row["member_name"]) is not None
        ]
        if not targets:
            raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[2], "generated target is unavailable")
        if case == "multiple_identity_classes":
            if len(targets) < 2:
                raise SuffixIdentityGrammarRefusal(
                    REFUSAL_ROUTES[2], "generated targets are unavailable"
                )
            targets[0]["member_name"] = _mutate_name(
                targets[0]["member_name"], "prefix_segment_grammar"
            )
            targets[1]["member_name"] = _mutate_name(
                targets[1]["member_name"], "filename_subject_disagreement"
            )
        else:
            targets[0]["member_name"] = _mutate_name(targets[0]["member_name"], case)
        return changed
    except (ValueError, StopIteration, vr12a.P15RunIndexRepairRefusal) as exc:
        raise SuffixIdentityGrammarRefusal(
            REFUSAL_ROUTES[2], "generated witness construction refused"
        ) from exc


def _p15_names(source: Mapping[str, Any]) -> list[str]:
    names: list[str] = []
    entries = source.get("entries")
    if not isinstance(entries, list):
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[2], "generated source entries differ")
    for row in entries:
        if (
            isinstance(row, dict)
            and row.get("entry_kind") == "regular_file"
            and isinstance(row.get("member_name"), str)
            and any(
                row["member_name"].endswith(value) for value in vr12a.selector.REQUIRED_SUFFIXES
            )
            and vr12a._repaired_core_match(row["member_name"]) is None
        ):
            names.append(row["member_name"])
    return names


def discriminate_generated_source(source: Mapping[str, Any]) -> GrammarDecision:
    """Call unchanged VR12A once, then emit one aggregate generated route."""

    before = vr12a.vr2._canonical_source_bytes(source)
    try:
        vr12a.adapt_repaired_source(source)
    except vr12a.P15RunIndexRepairRefusal as exc:
        if (exc.route, exc.safe_reason) != EXPECTED_P15:
            raise SuffixIdentityGrammarRefusal(
                REFUSAL_ROUTES[2], "VR12A route is outside frozen P15"
            ) from exc
        routes = {_classify_identity_name(name) for name in _p15_names(source)}
        if not routes:
            raise SuffixIdentityGrammarRefusal(
                REFUSAL_ROUTES[2], "generated P15 witness is unavailable"
            )
        route = RESULT_ROUTES[15] if len(routes) > 1 else next(iter(routes))
    else:
        route = SUCCESS_ROUTE
    if vr12a.vr2._canonical_source_bytes(source) != before:
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[2], "VR12A changed generated source")
    return GrammarDecision(route=route)


def _run_matrix() -> dict[str, Any]:
    route_counts: Counter[str] = Counter()
    replay_rows: list[list[list[str]]] = []
    generated_input_bytes = 0
    calls = 0
    for _replay in range(REPLAYS):
        current: list[list[str]] = []
        for order in ORDERS:
            for case in CASES:
                source = _build_case(case, order)
                before = vr12a.vr2._canonical_source_bytes(source)
                generated_input_bytes += len(before)
                decision = discriminate_generated_source(source)
                calls += 1
                if decision.route != CASE_ROUTES[case]:
                    raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[3], "generated route differs")
                if vr12a.vr2._canonical_source_bytes(source) != before:
                    raise SuffixIdentityGrammarRefusal(
                        REFUSAL_ROUTES[3], "generated source changed"
                    )
                route_counts[decision.route] += 1
                current.append([case, order, decision.route])
        replay_rows.append(current)
    matrix = {
        "route_counts": dict(sorted(route_counts.items())),
        "replay_digests": [_sha256_bytes(_canonical_json_bytes(rows)) for rows in replay_rows],
        "matrix_digest_sha256": _sha256_bytes(_canonical_json_bytes(replay_rows[0])),
        "generated_input_bytes": generated_input_bytes,
        "path_count": len(CASES) * len(ORDERS) * REPLAYS,
        "VR12A_calls": calls,
        "source_mutations_by_VR12A": 0,
        "single_class_paths": len(SINGLE_CLASS_CASES) * len(ORDERS) * REPLAYS,
        "multiple_class_paths": len(ORDERS) * REPLAYS,
        "control_paths": len(ORDERS) * REPLAYS,
    }
    _validate_matrix(matrix)
    return matrix


def _expected_route_counts() -> dict[str, int]:
    return {route: 4 for route in (SUCCESS_ROUTE, *RESULT_ROUTES)}


def _validate_matrix(matrix: Mapping[str, Any]) -> None:
    expected_fields = {
        "route_counts",
        "replay_digests",
        "matrix_digest_sha256",
        "generated_input_bytes",
        "path_count",
        "VR12A_calls",
        "source_mutations_by_VR12A",
        "single_class_paths",
        "multiple_class_paths",
        "control_paths",
    }
    digests = matrix.get("replay_digests")
    if (
        set(matrix) != expected_fields
        or matrix.get("route_counts") != _expected_route_counts()
        or matrix.get("path_count") != 68
        or matrix.get("VR12A_calls") != 68
        or matrix.get("source_mutations_by_VR12A") != 0
        or matrix.get("single_class_paths") != 60
        or matrix.get("multiple_class_paths") != 4
        or matrix.get("control_paths") != 4
        or not isinstance(matrix.get("generated_input_bytes"), int)
        or matrix.get("generated_input_bytes", 0) <= 0
        or not isinstance(digests, list)
        or len(digests) != 2
        or digests[0] != digests[1]
        or any(not isinstance(value, str) or len(value) != 64 for value in digests)
        or matrix.get("matrix_digest_sha256") != digests[0]
    ):
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[3], "matrix result differs")


def _validate_thread_environment(
    environment: Mapping[str, str] | None = None,
) -> None:
    values = os.environ if environment is None else environment
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[5], "thread environment differs")


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).casefold() in FORBIDDEN_PUBLIC_KEYS:
                raise SuffixIdentityGrammarRefusal(
                    REFUSAL_ROUTES[4], "aggregate output key is forbidden"
                )
            _walk_public(item)
    elif isinstance(value, list):
        for item in value:
            _walk_public(item)
    elif isinstance(value, str):
        lowered = value.casefold()
        if (
            ".codex_work" in lowered
            or "/users/" in lowered
            or "private_manifest" in lowered
            or "safe_reason" in lowered
        ):
            raise SuffixIdentityGrammarRefusal(
                REFUSAL_ROUTES[4], "aggregate output value is forbidden"
            )


def _assert_resources(
    *,
    runtime_seconds: float,
    peak_rss_bytes: int,
    generated_input_bytes: int,
    aggregate_output_bytes: int,
    retained_output_bytes: int,
    contract: Mapping[str, Any],
) -> None:
    caps = contract["resource_caps"]
    values = (
        runtime_seconds,
        peak_rss_bytes,
        generated_input_bytes,
        aggregate_output_bytes,
        retained_output_bytes,
    )
    if any(
        isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0
        for value in values
    ):
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[5], "resource measurement differs")
    if (
        runtime_seconds > caps["runtime_seconds_maximum"]
        or peak_rss_bytes >= caps["peak_RSS_bytes_maximum"]
        or generated_input_bytes > caps["generated_input_bytes_maximum"]
        or aggregate_output_bytes > caps["aggregate_output_bytes_maximum"]
        or retained_output_bytes != caps["retained_generated_output_bytes"]
    ):
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[5], "resource cap exceeded")


def _expect_refusal(
    name: str,
    expected_route: str,
    action: Callable[[], Any],
    counts: dict[str, str],
) -> None:
    try:
        action()
    except SuffixIdentityGrammarRefusal as exc:
        if exc.route != expected_route:
            raise SuffixIdentityGrammarRefusal(
                REFUSAL_ROUTES[3], "direct refusal route differs"
            ) from exc
        counts[name] = exc.route
        return
    raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[3], "direct mutation unexpectedly passed")


def _run_direct_refusals(
    *,
    contract: Mapping[str, Any],
    payloads: Mapping[str, bytes],
    matrix: Mapping[str, Any],
) -> dict[str, str]:
    refusals: dict[str, str] = {}
    contract_mutations: tuple[Any, ...] = (
        {**contract, "schema_version": "9.9.9"},
        {**contract, "lane_id": "MARC2-VR15X"},
        {**contract, "status": "implemented"},
        {**contract, "unexpected": True},
        [],
    )
    for index, mutation in enumerate(contract_mutations, start=1):
        _expect_refusal(
            f"contract_drift_{index:02d}",
            REFUSAL_ROUTES[0],
            lambda value=mutation: _verify_contract_mapping(value),
            refusals,
        )
    for index, mutation in enumerate(
        (
            {"commit": "0" * 40},
            {"ci_run_id": 0},
            {"base_job_id": 0},
            {"optional_job_id": 0},
        ),
        start=1,
    ):
        _expect_refusal(
            f"registration_proof_drift_{index:02d}",
            REFUSAL_ROUTES[0],
            lambda values=mutation: _verify_registration_proof(**values),
            refusals,
        )
    for index, path in enumerate(payloads, start=1):
        changed = dict(payloads)
        changed[path] = changed[path] + b"x"
        _expect_refusal(
            f"fixed_artifact_drift_{index:02d}",
            REFUSAL_ROUTES[1],
            lambda values=changed: _verify_fixed_payloads(contract, values),
            refusals,
        )
    for index, name in enumerate(
        (
            "ordinary.bin",
            ("Freewill_generated/sub-01/ses-01/eeg/sub-01_ses-01_task-freewill_run-01_eeg.eeg"),
            "unsafe//sub-01_ses-01_task-freewill_run-x_eeg.eeg",
        ),
        start=1,
    ):
        _expect_refusal(
            f"classifier_refusal_{index:02d}",
            REFUSAL_ROUTES[2],
            lambda value=name: _classify_identity_name(value),
            refusals,
        )
    matrix_mutations: list[dict[str, Any]] = []
    for route in (SUCCESS_ROUTE, *RESULT_ROUTES):
        changed = copy.deepcopy(dict(matrix))
        changed["route_counts"][route] = 3
        matrix_mutations.append(changed)
    for key, value in (
        ("path_count", 67),
        ("VR12A_calls", 67),
        ("source_mutations_by_VR12A", 1),
        ("single_class_paths", 59),
        ("multiple_class_paths", 3),
        ("control_paths", 3),
    ):
        changed = copy.deepcopy(dict(matrix))
        changed[key] = value
        matrix_mutations.append(changed)
    for index, changed in enumerate(matrix_mutations, start=1):
        _expect_refusal(
            f"matrix_drift_{index:02d}",
            REFUSAL_ROUTES[3],
            lambda value=changed: _validate_matrix(value),
            refusals,
        )
    for index, key in enumerate(sorted(FORBIDDEN_PUBLIC_KEYS)[:15], start=1):
        _expect_refusal(
            f"public_firewall_{index:02d}",
            REFUSAL_ROUTES[4],
            lambda value={key: "redacted"}: _walk_public(value),
            refusals,
        )
    base_resources: dict[str, int | float] = {
        "runtime_seconds": 1.0,
        "peak_rss_bytes": 1,
        "generated_input_bytes": 1,
        "aggregate_output_bytes": 1,
        "retained_output_bytes": 0,
    }
    for index, mutation in enumerate(
        (
            {"runtime_seconds": 31.0},
            {"peak_rss_bytes": 268_435_456},
            {"generated_input_bytes": 33_554_433},
            {"aggregate_output_bytes": 1_048_577},
            {"retained_output_bytes": 1},
            {"runtime_seconds": -1.0},
        ),
        start=1,
    ):
        _expect_refusal(
            f"resource_refusal_{index:02d}",
            REFUSAL_ROUTES[5],
            lambda values={**base_resources, **mutation}: _assert_resources(
                **values, contract=contract
            ),
            refusals,
        )
    for index, environment in enumerate(
        (
            {},
            {**THREAD_ENVIRONMENT, "OMP_NUM_THREADS": "2"},
            {**THREAD_ENVIRONMENT, "OPENBLAS_NUM_THREADS": "0"},
        ),
        start=1,
    ):
        _expect_refusal(
            f"thread_refusal_{index:02d}",
            REFUSAL_ROUTES[5],
            lambda value=environment: _validate_thread_environment(value),
            refusals,
        )
    if len(refusals) < contract["direct_refusal_minimum"]:
        raise SuffixIdentityGrammarRefusal(
            REFUSAL_ROUTES[3], "direct refusal coverage is incomplete"
        )
    return dict(sorted(refusals.items()))


def _zero_counters() -> dict[str, int]:
    return {
        "private_or_Git_ignored_path_operations": 0,
        "consumed_VR13P_or_VR14P_path_or_output_operations": 0,
        "real_structural_source_or_private_manifest_operations": 0,
        "archive_or_neural_payload_operations": 0,
        "target_model_prediction_or_score_operations": 0,
        "FW2_or_CIL1_operations": 0,
        "network_provider_or_language_model_operations": 0,
        "device_or_hardware_operations": 0,
        "operations_on_other_projects": 0,
        "retry_rerun_resume_operations": 0,
        "release_or_scientific_claim_upgrades": 0,
    }


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def _stabilize_output_size(report: dict[str, Any]) -> int:
    for _ in range(10):
        size = len(_canonical_json_bytes(report))
        if report["measurements"]["aggregate_output_bytes"] == size:
            return size
        report["measurements"]["aggregate_output_bytes"] = size
    raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[3], "aggregate output size did not stabilize")


def _validate_public_report(report: Mapping[str, Any]) -> None:
    expected_fields = {
        "schema_name",
        "schema_version",
        "lane_id",
        "route",
        "status",
        "registration_proof",
        "route_summary",
        "replay_summary",
        "mechanics",
        "measurements",
        "direct_refusals",
        "warnings",
        "access_counters",
        "acceptance_gates",
        "next_gate",
        "claim_boundary",
    }
    if (
        set(report) != expected_fields
        or report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != SUCCESS_ROUTE
        or report.get("status") != "generated_qualification_passed"
        or report.get("route_summary", {}).get("route_counts") != _expected_route_counts()
        or report.get("replay_summary", {}).get("total_paths") != 68
        or report.get("replay_summary", {}).get("exact_VR12A_calls") != 68
        or len(report.get("direct_refusals", {})) < 70
        or not all(report.get("acceptance_gates", {}).values())
        or not all(value == 0 for value in report.get("access_counters", {}).values())
    ):
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[3], "aggregate report differs")
    _walk_public(report)
    if len(_canonical_json_bytes(report)) != report["measurements"]["aggregate_output_bytes"]:
        raise SuffixIdentityGrammarRefusal(REFUSAL_ROUTES[3], "aggregate output byte count differs")


def qualify_generated(
    *,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Run the bounded 68-path generated qualification in memory."""

    _validate_thread_environment(environment)
    start = clock()
    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    _verify_registration_proof()
    payloads = _fixed_payloads(contract)
    fixed_input_bytes = _verify_fixed_payloads(contract, payloads)
    static_guard_count = _verify_static_grammar(contract, payloads)
    matrix = _run_matrix()
    direct_refusals = _run_direct_refusals(contract=contract, payloads=payloads, matrix=matrix)
    runtime_seconds = clock() - start
    peak_rss_bytes = rss_reader()
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": SUCCESS_ROUTE,
        "status": "generated_qualification_passed",
        "registration_proof": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_jobs_green": True,
        },
        "route_summary": {
            "ordered_routes": [SUCCESS_ROUTE, *RESULT_ROUTES],
            "route_counts": matrix["route_counts"],
            "one_route_per_generated_source": True,
            "failure_details_retained": 0,
            "per_source_outcomes_retained": 0,
        },
        "replay_summary": {
            "generated_cases": len(CASES),
            "source_orders": len(ORDERS),
            "exact_replays": REPLAYS,
            "total_paths": matrix["path_count"],
            "exact_VR12A_calls": matrix["VR12A_calls"],
            "byte_identical_replay": True,
            "order_invariant_routes": True,
            "internal_matrix_digest_sha256": matrix["matrix_digest_sha256"],
        },
        "mechanics": {
            "entry_count_each": 1_227,
            "static_P15_guard_call_sites": static_guard_count,
            "single_class_P15_paths": matrix["single_class_paths"],
            "multiple_class_P15_paths": matrix["multiple_class_paths"],
            "control_paths": matrix["control_paths"],
            "post_VR12A_source_mutations": 0,
            "source_mutations_by_VR12A": matrix["source_mutations_by_VR12A"],
            "predecessor_modules_modified": 0,
        },
        "measurements": {
            "fixed_artifact_count": 12,
            "fixed_artifact_bytes": fixed_input_bytes + CONTRACT_BYTES,
            "generated_input_bytes": matrix["generated_input_bytes"],
            "aggregate_output_bytes": 0,
            "retained_generated_output_bytes": 0,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_structural_metadata_only",
            "end_to_end_latency_measured": False,
        },
        "direct_refusals": direct_refusals,
        "warnings": [
            "consumed_private_identity_class_remains_unavailable",
            "real_cohort_remains_unavailable",
            "neural_payload_not_accessed",
            "generated_routes_have_no_scientific_claim_value",
        ],
        "access_counters": _zero_counters(),
        "acceptance_gates": {
            "fixed_inputs_match": True,
            "exact_repaired_regex_and_P15_guard_static_bound": True,
            "sixteen_ordered_result_routes_unique": True,
            "all_68_paths_called_unchanged_VR12A_once": True,
            "all_single_witnesses_reached_exact_P15": True,
            "every_route_observed_four_times": True,
            "canonical_reversed_and_replays_match": True,
            "source_immutable": True,
            "direct_refusal_minimum_passed": True,
            "retained_output_zero": True,
            "resource_caps_passed": True,
            "forbidden_operations_zero": True,
        },
        "next_gate": {
            "generated_implementation_complete": True,
            "remote_implementation_proof_required_before_Tier_C_request": True,
            "future_private_discriminator_authorized": False,
            "consumed_VR13P_or_VR14P_reuse_allowed": False,
            "MARC2_FW2_or_CIL1_authorized": False,
        },
        "claim_boundary": {
            "engineering_ceiling": (
                "generated deterministic discrimination of fifteen suffix identity "
                "grammar classes plus one multiple-class route"
            ),
            "scientific_ceiling": "none",
            "private_cause_identified": False,
            "real_cohort_frozen": False,
            "neural_effect_established": False,
            "decoding_accuracy_established": False,
            "language_or_thought_decoding_established": False,
            "live_decoding_established": False,
        },
    }
    output_bytes = _stabilize_output_size(report)
    _assert_resources(
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        generated_input_bytes=matrix["generated_input_bytes"],
        aggregate_output_bytes=output_bytes,
        retained_output_bytes=0,
        contract=contract,
    )
    _validate_public_report(report)
    return report


def build_plan_summary() -> dict[str, Any]:
    """Return the frozen generated-only plan without running the matrix."""

    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    return {
        "lane_id": LANE_ID,
        "status": contract["status"],
        "fixed_input_count": contract["fixed_input_count"],
        "fixed_input_bytes": contract["fixed_input_bytes"],
        "generated_cases": len(CASES),
        "required_paths": contract["generated_matrix"]["required_paths"],
        "required_VR12A_calls": contract["generated_matrix"]["required_VR12A_calls"],
        "ordered_routes": [SUCCESS_ROUTE, *RESULT_ROUTES],
        "direct_refusal_minimum": contract["direct_refusal_minimum"],
        "private_access_authorized": False,
        "network_bytes": 0,
        "real_or_private_bytes": 0,
        "MARC2_FW2_or_CIL1_authorized": False,
    }


def build_inspection_summary() -> dict[str, Any]:
    """Inspect only the committed registration and proof boundary."""

    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    _verify_registration_proof()
    return {
        "lane_id": LANE_ID,
        "contract_sha256": CONTRACT_SHA256,
        "registration_commit": GREEN_REGISTRATION_COMMIT,
        "registration_CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
        "both_jobs_green": True,
        "grammar_class_count": len(RESULT_ROUTES),
        "private_access_authorized": False,
        "scientific_ceiling": "none",
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="show the frozen generated-only plan")
    subparsers.add_parser("inspect", help="inspect the registration proof")
    subparsers.add_parser("qualify", help="run the in-memory generated matrix")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "plan":
        payload = build_plan_summary()
    elif args.command == "inspect":
        payload = build_inspection_summary()
    else:
        payload = qualify_generated()
    sys.stdout.buffer.write(_canonical_json_bytes(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
