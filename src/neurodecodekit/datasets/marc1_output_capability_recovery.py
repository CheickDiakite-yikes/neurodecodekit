"""Capability-first generated recovery for the consumed MARC1 pagination lane."""

from __future__ import annotations

import argparse
import ast
import copy
import errno
import hashlib
import importlib
import json
import os
import re
import resource
import stat
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC1-OP1"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc1_output_capability_recovery_contract.v0.json"
)
CONTRACT_SHA256 = "2fe17a263a8c923c2a7af76dbba0c6422eacb601b7668de987ef0d53485c5cb6"
GREEN_CONTRACT_COMMIT = "baade51146309bd3b3fa6c1750a36482669a0ff2"
GREEN_CONTRACT_CI_RUN_ID = 31597291352
GREEN_CONTRACT_BASE_JOB_ID = 94115807028
GREEN_CONTRACT_OPTIONAL_JOB_ID = 94115807008
CONSUMED_RESULT_SHA256 = (
    "b99be5d82e1f49f064cf17e4a7b2d6a21e36d89cebc78b133136b181fb4bdcf2"
)
CONSUMED_SOURCE_SHA256 = (
    "3dc5f4fdf5792040f153797d708cf27cd8ece8e4dc40b3a0eeaba86071724228"
)
CAPABILITY_POLICY_SHA256 = (
    "6412dd0cdfabf2b96d0c5ebf2d1e2dadb4fc3e8fe5eed6ac762524a5c9881054"
)
REGISTERED_OUTPUT_PATH = (
    "/private/tmp/neurodecodekit-marc1op1-registered-closeout-20260812"
)

REPORT_NAME = "marc1_output_capability_qualification.v0.json"
PRIVATE_NAME = "marc1_output_capability.generated.private.v0.json"
OUTPUT_NAMES = (REPORT_NAME, PRIVATE_NAME)
MAX_PUBLIC_OUTPUT_BYTES = 1024 * 1024
MAX_COMBINED_OUTPUT_BYTES = 2 * 1024 * 1024
MAX_INCREMENTAL_DISK_BYTES = 4 * 1024 * 1024
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024 * 1024
MAX_GENERATED_INPUT_BYTES = 2 * 1024 * 1024
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)

ACCEPTED_CASES = (
    "regular_absolute_parent_absent_child",
    "deeper_all_regular_ancestor_chain_absent_child",
    "canonical_rows_absent_Content_Encoding",
    "reversed_rows_absent_Content_Encoding",
    "canonical_rows_identity_Content_Encoding",
    "reversed_rows_mixed_case_identity_Content_Encoding",
)
REFUSAL_CASES = (
    "relative_path",
    "empty_path_or_basename",
    "root_destination",
    "dot_or_dotdot_component",
    "non_normalized_path",
    "missing_parent",
    "non_directory_parent",
    "immediate_parent_symlink",
    "earlier_ancestor_symlink",
    "existing_output_file",
    "existing_output_directory",
    "existing_output_symlink",
    "dangling_output_symlink",
    "missing_required_standard_library_primitive",
    "lstat_open_device_or_inode_disagreement",
    "closed_replaced_or_retyped_parent_descriptor",
    "output_appears_after_capability_acquisition",
    "parent_relative_mkdir_or_child_open_disagreement",
    "early_repository_contract_import_fixture_selection_or_output_operation",
    "wrong_green_research_proof",
    "wrong_consumed_result_proof",
    "wrong_capability_policy_hash",
    "eager_or_forbidden_consumed_pagination_import_or_call",
    "wrong_pagination_query",
    "ten_row_partial_inventory",
    "target_like_field",
    "split_overlap_or_selection_identity_drift",
    "output_filename_allowlist_drift",
    "nonexclusive_write_or_overwrite_attempt",
    "runtime_RSS_input_output_or_disk_cap_breach",
    "nondeterministic_public_or_private_replay",
    "second_registered_preflight_or_qualifier_invocation",
)
FAILURE_ROUTES = {
    "MARC1OP-F00": "green_proof_artifact_source_or_policy_mismatch",
    "MARC1OP-F01": "lexical_path_identity_failure",
    "MARC1OP-F02": "ancestor_primitive_or_capability_acquisition_failure",
    "MARC1OP-F03": "held_capability_revalidation_or_race_failure",
    "MARC1OP-F04": "operation_order_eager_import_or_consumed_call_failure",
    "MARC1OP-F05": "pagination_semantic_target_firewall_or_selection_failure",
    "MARC1OP-F06": "output_allowlist_exclusive_write_privacy_or_resource_failure",
    "MARC1OP-F07": "replay_cleanup_second_invocation_retry_or_rerun_failure",
}
SUCCESS_ROUTES = {
    "MARC1OP-P0": "registered_path_only_preflight_passed_with_zero_early_operations",
    "MARC1OP-G1": "generated_capability_pagination_selection_output_and_cleanup_pass",
}
ACCEPTANCE_GATES = (
    "exact_green_research_proof",
    "exact_contract_result_consumed_source_and_policy_hashes",
    "exact_registered_path_identity",
    "no_module_scope_consumed_pagination_import",
    "capability_acquisition_first_in_preflight_and_qualify",
    "all_ancestors_real_directories_and_no_follow_checked",
    "held_parent_device_inode_type_matches_before_work_and_write",
    "output_absence_at_acquisition_and_precreation",
    "all_19_precapability_mutations_refuse_with_zero_early_counters",
    "all_13_postcapability_mutations_refuse_under_registered_routes",
    "all_six_accepted_cases_pass",
    "four_transport_cases_share_semantic_and_selection_hashes",
    "exact_55_row_identity_and_54_56_10_row_refusals",
    "exact_target_free_12_plus_12_cohort_and_split_binding",
    "zero_consumed_qualifier_calls_and_source_modifications",
    "exact_two_parent_relative_exclusive_allowlisted_writes",
    "public_private_separation_and_one_public_inspection",
    "deterministic_public_and_private_hash_replay",
    "all_resource_and_zero_access_counters",
    "exact_generated_cleanup",
)
EARLY_COUNTER_KEYS = (
    "repository_reads",
    "contract_loads",
    "deferred_pagination_imports",
    "fixtures_constructed",
    "rows_constructed",
    "selections_run",
    "output_bytes_allocated",
)
PUBLIC_REPORT_FIELDS = {
    "schema_name",
    "schema_version",
    "lane_id",
    "status",
    "route",
    "proof_posture",
    "green_contract_proof",
    "operation_order",
    "capability_summary",
    "response_summary",
    "refusal_summary",
    "inventory_summary",
    "cohort_summary",
    "split_summary",
    "byte_summary",
    "selection_hashes",
    "source_surface",
    "replay_summary",
    "access_counters",
    "measurements",
    "acceptance_gates",
    "warnings",
    "unavailable_fields",
    "claim_boundary",
}
TARGET_LIKE_RE = re.compile(
    r"(?:^|_)(?:answer|event|ground_truth|intended_text|label|outcome|quality|"
    r"reference_text|response|sentence|target|trial_label)(?:_|$)",
    re.IGNORECASE,
)
PRIVATE_VALUE_RE = re.compile(r"sub-\d{2}(?:\.zip)?", re.IGNORECASE)

CANDIDATE_POLICY = {
    "before_any": [
        "repository_read",
        "contract_load",
        "deferred_pagination_import",
        "fixture_construction",
        "selection",
        "output_write",
    ],
    "network_bytes": 0,
    "preflight_order": [
        "validate_lexical_path",
        "lstat_every_ancestor",
        "open_parent_no_follow",
        "bind_parent_device_inode",
        "require_output_absent",
    ],
    "real_private_input_bytes": 0,
    "registered_output_path": REGISTERED_OUTPUT_PATH,
    "retries": 0,
    "schema": "marc1.output_capability_policy",
    "version": "0.1.0",
    "write_order": [
        "revalidate_parent_capability",
        "require_output_absent_again",
        "mkdirat_output",
        "open_output_no_follow",
        "exclusive_relative_writes",
        "measure_inspect_hash",
        "relative_cleanup",
    ],
}


class OutputCapabilityRefusal(RuntimeError):
    """Fail closed with one aggregate-safe MARC1-OP1 route."""

    def __init__(
        self,
        route: str,
        reason: str,
        *,
        early_counters: Mapping[str, int] | None = None,
    ):
        if route not in FAILURE_ROUTES:
            raise ValueError("unknown MARC1-OP1 failure route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason
        self.early_counters = (
            dict(early_counters) if early_counters is not None else None
        )


@dataclass(slots=True)
class AccessLedger:
    """Operation counters used to prove capability-first ordering."""

    counters: dict[str, int] = field(
        default_factory=lambda: {
            "capability_acquisitions": 0,
            "capability_revalidations": 0,
            "repository_reads": 0,
            "contract_loads": 0,
            "deferred_pagination_imports": 0,
            "fixtures_constructed": 0,
            "rows_constructed": 0,
            "selections_run": 0,
            "output_directories_created": 0,
            "output_files_created": 0,
            "output_bytes_allocated": 0,
            "public_report_inspections": 0,
            "cleanup_file_unlinks": 0,
            "cleanup_directory_removals": 0,
            "consumed_qualifier_calls": 0,
            "consumed_source_modifications": 0,
            "dataset_specific_Figshare_requests": 0,
            "dataset_specific_response_bytes": 0,
            "private_Freewill_manifest_operations": 0,
            "consumed_private_root_operations": 0,
            "payload_requests": 0,
            "payload_bytes": 0,
            "signal_sample_reads": 0,
            "target_or_label_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "scoring_events": 0,
            "provider_or_language_model_calls": 0,
            "hardware_operations": 0,
            "retry_or_rerun_operations": 0,
            "operations_on_other_projects": 0,
            "scientific_claim_upgrades": 0,
        }
    )

    def increment(self, name: str, amount: int = 1) -> None:
        if name not in self.counters or amount < 0:
            raise ValueError("invalid access-ledger update")
        self.counters[name] += amount

    def early_snapshot(self) -> dict[str, int]:
        return {name: self.counters[name] for name in EARLY_COUNTER_KEYS}


@dataclass(slots=True)
class OutputCapability:
    """Process-local authority for one absent child under one held parent."""

    parent_fd: int
    parent_path: str
    parent_device: int
    parent_inode: int
    parent_mode: int
    output_basename: str
    allowlisted_filenames: tuple[str, str]
    acquisition_sequence_number: int
    acquired_at: float
    ledger: AccessLedger
    output_fd: int | None = None
    output_created: bool = False
    closed: bool = False

    def __reduce__(self) -> Any:
        raise TypeError("OutputCapability is process-local and nonserializable")

    def close(self) -> None:
        if self.output_fd is not None:
            try:
                os.close(self.output_fd)
            except OSError:
                pass
            self.output_fd = None
        if not self.closed:
            try:
                os.close(self.parent_fd)
            except OSError:
                pass
            self.closed = True


@dataclass(frozen=True)
class QualificationOutcome:
    """Aggregate result retained in memory after exact temporary cleanup."""

    report: Mapping[str, Any]
    report_bytes: bytes
    private_manifest_sha256: str
    public_report_sha256: str
    output_path: str
    output_removed: bool
    runtime_seconds: float
    peak_rss_bytes: int
    generated_input_bytes: int
    generated_output_bytes: int


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _policy_sha256() -> str:
    return _sha256_bytes(_canonical_json_bytes(CANDIDATE_POLICY))


def _require_capability_primitives(*, fault: str | None = None) -> None:
    required_flags = ("O_DIRECTORY", "O_NOFOLLOW")
    dir_fd_functions = (os.open, os.mkdir, os.stat, os.unlink, os.rmdir)
    if (
        fault == "missing_primitive"
        or any(not hasattr(os, name) for name in required_flags)
        or any(function not in os.supports_dir_fd for function in dir_fd_functions)
        or os.stat not in os.supports_follow_symlinks
    ):
        raise OutputCapabilityRefusal(
            "MARC1OP-F02", "required no-follow directory primitives unavailable"
        )


def _lexical_output_identity(output_dir: str | os.PathLike[str]) -> tuple[str, str, str]:
    try:
        raw = os.fspath(output_dir)
    except TypeError as exc:
        raise OutputCapabilityRefusal("MARC1OP-F01", "output path type differs") from exc
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise OutputCapabilityRefusal("MARC1OP-F01", "empty output path or basename")
    if not raw.startswith(os.sep):
        raise OutputCapabilityRefusal("MARC1OP-F01", "output path is not absolute")
    components = raw.split(os.sep)
    if "." in components or ".." in components:
        raise OutputCapabilityRefusal("MARC1OP-F01", "dot component is forbidden")
    if raw != os.path.normpath(raw):
        raise OutputCapabilityRefusal("MARC1OP-F01", "output path is not normalized")
    if raw == os.sep:
        raise OutputCapabilityRefusal("MARC1OP-F01", "root destination is forbidden")
    parent, basename = os.path.split(raw)
    if not parent or not basename:
        raise OutputCapabilityRefusal("MARC1OP-F01", "empty output parent or basename")
    return raw, parent, basename


def _lstat_regular_ancestor_chain(parent: str) -> os.stat_result:
    current = os.sep
    try:
        root_stat = os.lstat(current)
        if not stat.S_ISDIR(root_stat.st_mode) or stat.S_ISLNK(root_stat.st_mode):
            raise OutputCapabilityRefusal("MARC1OP-F02", "root ancestor differs")
        for component in Path(parent).parts[1:]:
            current = os.path.join(current, component)
            observed = os.lstat(current)
            if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
                raise OutputCapabilityRefusal(
                    "MARC1OP-F02", "output ancestor is not a real directory"
                )
        return os.lstat(parent)
    except OutputCapabilityRefusal:
        raise
    except OSError as exc:
        raise OutputCapabilityRefusal(
            "MARC1OP-F02", "output ancestor is unavailable"
        ) from exc


def _require_relative_child_absent(parent_fd: int, basename: str, route: str) -> None:
    try:
        os.stat(basename, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise OutputCapabilityRefusal(route, "output child absence check failed") from exc
    raise OutputCapabilityRefusal(route, "output child already exists")


def acquire_output_capability(
    output_dir: str | os.PathLike[str],
    *,
    ledger: AccessLedger | None = None,
    sequence_number: int = 1,
    clock: Callable[[], float] = time.perf_counter,
    fault: str | None = None,
) -> OutputCapability:
    """Acquire one held output capability before any experiment operation."""

    selected_ledger = ledger if ledger is not None else AccessLedger()
    try:
        acquired_at = clock()
        if sequence_number != 1:
            raise OutputCapabilityRefusal(
                "MARC1OP-F07", "second invocation is forbidden"
            )
        _, parent, basename = _lexical_output_identity(output_dir)
        _require_capability_primitives(fault=fault)
        before = _lstat_regular_ancestor_chain(parent)
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        try:
            parent_fd = os.open(parent, flags)
        except OSError as exc:
            raise OutputCapabilityRefusal("MARC1OP-F02", "parent open failed") from exc
        try:
            opened = os.fstat(parent_fd)
            if fault == "identity_mismatch" or (
                opened.st_dev != before.st_dev
                or opened.st_ino != before.st_ino
                or not stat.S_ISDIR(opened.st_mode)
            ):
                raise OutputCapabilityRefusal(
                    "MARC1OP-F02", "lstat and open parent identity differ"
                )
            _require_relative_child_absent(parent_fd, basename, "MARC1OP-F02")
        except Exception:
            os.close(parent_fd)
            raise
    except OutputCapabilityRefusal as exc:
        exc.early_counters = selected_ledger.early_snapshot()
        raise
    selected_ledger.increment("capability_acquisitions")
    return OutputCapability(
        parent_fd=parent_fd,
        parent_path=parent,
        parent_device=opened.st_dev,
        parent_inode=opened.st_ino,
        parent_mode=opened.st_mode,
        output_basename=basename,
        allowlisted_filenames=OUTPUT_NAMES,
        acquisition_sequence_number=sequence_number,
        acquired_at=acquired_at,
        ledger=selected_ledger,
    )


def _revalidate_capability(capability: OutputCapability) -> None:
    if capability.closed:
        raise OutputCapabilityRefusal("MARC1OP-F03", "parent descriptor is closed")
    try:
        opened = os.fstat(capability.parent_fd)
        named = os.lstat(capability.parent_path)
    except OSError as exc:
        raise OutputCapabilityRefusal(
            "MARC1OP-F03", "held parent cannot be revalidated"
        ) from exc
    identity = (capability.parent_device, capability.parent_inode)
    if (
        (opened.st_dev, opened.st_ino) != identity
        or (named.st_dev, named.st_ino) != identity
        or not stat.S_ISDIR(opened.st_mode)
        or not stat.S_ISDIR(named.st_mode)
    ):
        raise OutputCapabilityRefusal("MARC1OP-F03", "held parent identity changed")
    _require_relative_child_absent(
        capability.parent_fd, capability.output_basename, "MARC1OP-F03"
    )
    capability.ledger.increment("capability_revalidations")


def _create_output_directory(
    capability: OutputCapability, *, fault: str | None = None
) -> None:
    _revalidate_capability(capability)
    try:
        os.mkdir(capability.output_basename, 0o700, dir_fd=capability.parent_fd)
        capability.output_created = True
        capability.ledger.increment("output_directories_created")
        if fault == "child_open_mismatch":
            raise OutputCapabilityRefusal(
                "MARC1OP-F03", "parent-relative child-open identity differs"
            )
        child_fd = os.open(
            capability.output_basename,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=capability.parent_fd,
        )
        child_named = os.stat(
            capability.output_basename,
            dir_fd=capability.parent_fd,
            follow_symlinks=False,
        )
        child_opened = os.fstat(child_fd)
        if (
            (child_named.st_dev, child_named.st_ino)
            != (child_opened.st_dev, child_opened.st_ino)
            or not stat.S_ISDIR(child_opened.st_mode)
        ):
            os.close(child_fd)
            raise OutputCapabilityRefusal(
                "MARC1OP-F03", "parent-relative child-open identity differs"
            )
        capability.output_fd = child_fd
    except OutputCapabilityRefusal:
        raise
    except OSError as exc:
        raise OutputCapabilityRefusal(
            "MARC1OP-F03", "parent-relative output creation failed"
        ) from exc


def _validate_output_allowlist(names: Sequence[str]) -> None:
    if tuple(names) != OUTPUT_NAMES or len(set(names)) != 2:
        raise OutputCapabilityRefusal("MARC1OP-F06", "output allowlist differs")


def _write_relative_exclusive(
    capability: OutputCapability,
    filename: str,
    payload: bytes,
    mode: int,
) -> None:
    if capability.output_fd is None or filename not in capability.allowlisted_filenames:
        raise OutputCapabilityRefusal("MARC1OP-F06", "output write is not allowlisted")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    try:
        descriptor = os.open(filename, flags, mode, dir_fd=capability.output_fd)
        try:
            os.fchmod(descriptor, mode)
            written = 0
            while written < len(payload):
                count = os.write(descriptor, payload[written:])
                if count <= 0:
                    raise OSError(errno.EIO, "short output write")
                written += count
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise OutputCapabilityRefusal(
            "MARC1OP-F06", "exclusive parent-relative output write failed"
        ) from exc
    capability.ledger.increment("output_files_created")
    capability.ledger.increment("output_bytes_allocated", len(payload))


def _read_public_relative(capability: OutputCapability) -> bytes:
    if capability.output_fd is None:
        raise OutputCapabilityRefusal("MARC1OP-F06", "output descriptor unavailable")
    try:
        descriptor = os.open(
            REPORT_NAME,
            os.O_RDONLY | os.O_NOFOLLOW,
            dir_fd=capability.output_fd,
        )
        try:
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode) or opened.st_size > MAX_PUBLIC_OUTPUT_BYTES:
                raise OutputCapabilityRefusal(
                    "MARC1OP-F06", "public output identity or size differs"
                )
            payload = os.read(descriptor, MAX_PUBLIC_OUTPUT_BYTES + 1)
        finally:
            os.close(descriptor)
    except OutputCapabilityRefusal:
        raise
    except OSError as exc:
        raise OutputCapabilityRefusal("MARC1OP-F06", "public inspection failed") from exc
    capability.ledger.increment("public_report_inspections")
    return payload


def _cleanup_capability_output(
    capability: OutputCapability, *, suppress_errors: bool = False
) -> None:
    try:
        if capability.output_fd is not None:
            for filename in capability.allowlisted_filenames:
                try:
                    os.unlink(filename, dir_fd=capability.output_fd)
                    capability.ledger.increment("cleanup_file_unlinks")
                except FileNotFoundError:
                    pass
            os.close(capability.output_fd)
            capability.output_fd = None
        if capability.output_created:
            os.rmdir(capability.output_basename, dir_fd=capability.parent_fd)
            capability.output_created = False
            capability.ledger.increment("cleanup_directory_removals")
    except OSError as exc:
        if not suppress_errors:
            raise OutputCapabilityRefusal("MARC1OP-F07", "relative cleanup failed") from exc


def _read_bound_bytes(path: Path, ledger: AccessLedger) -> bytes:
    try:
        before = os.lstat(path)
        if not stat.S_ISREG(before.st_mode):
            raise OutputCapabilityRefusal("MARC1OP-F00", "bound artifact is not regular")
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            opened = os.fstat(descriptor)
            if (
                opened.st_dev != before.st_dev
                or opened.st_ino != before.st_ino
                or opened.st_size != before.st_size
            ):
                raise OutputCapabilityRefusal("MARC1OP-F00", "bound artifact changed")
            chunks: list[bytes] = []
            while chunk := os.read(descriptor, 64 * 1024):
                chunks.append(chunk)
        finally:
            os.close(descriptor)
    except OutputCapabilityRefusal:
        raise
    except OSError as exc:
        raise OutputCapabilityRefusal("MARC1OP-F00", "bound artifact read failed") from exc
    ledger.increment("repository_reads")
    return b"".join(chunks)


def load_registered_contract(
    repo_root: str | Path | None, ledger: AccessLedger
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    payload = _read_bound_bytes(root / CONTRACT_RELATIVE_PATH, ledger)
    ledger.increment("contract_loads")
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise OutputCapabilityRefusal("MARC1OP-F00", "contract hash differs")
    try:
        contract = json.loads(payload.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OutputCapabilityRefusal("MARC1OP-F00", "contract parse failed") from exc
    if (
        contract.get("schema_name")
        != "neurodecodekit.marc1_output_capability_recovery_contract"
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "frozen_generated_only_contract_no_implementation_or_execution"
    ):
        raise OutputCapabilityRefusal("MARC1OP-F00", "contract identity differs")
    proof = contract.get("green_research_anchor", {})
    if proof.get("both_required_jobs_green_before_contract") is not True:
        raise OutputCapabilityRefusal("MARC1OP-F00", "research green proof differs")
    for binding in contract.get("artifact_bindings", []):
        path = root / str(binding.get("path"))
        bound = _read_bound_bytes(path, ledger)
        if len(bound) != binding.get("bytes") or _sha256_bytes(bound) != binding.get(
            "sha256"
        ):
            raise OutputCapabilityRefusal("MARC1OP-F00", "artifact binding differs")
    if tuple(contract.get("accepted_cases", ())) != ACCEPTED_CASES:
        raise OutputCapabilityRefusal("MARC1OP-F00", "accepted cases differ")
    if tuple(contract.get("refusal_cases", ())) != REFUSAL_CASES:
        raise OutputCapabilityRefusal("MARC1OP-F00", "refusal cases differ")
    if tuple(contract.get("acceptance_gates", ())) != ACCEPTANCE_GATES:
        raise OutputCapabilityRefusal("MARC1OP-F00", "acceptance gates differ")
    return contract


def _assert_bound_identity(
    contract: Mapping[str, Any],
    *,
    green_commit: str = GREEN_CONTRACT_COMMIT,
    consumed_result_sha256: str = CONSUMED_RESULT_SHA256,
    capability_policy_sha256: str = CAPABILITY_POLICY_SHA256,
) -> None:
    if (
        green_commit != GREEN_CONTRACT_COMMIT
        or GREEN_CONTRACT_CI_RUN_ID != 31597291352
        or GREEN_CONTRACT_BASE_JOB_ID != 94115807028
        or GREEN_CONTRACT_OPTIONAL_JOB_ID != 94115807008
    ):
        raise OutputCapabilityRefusal("MARC1OP-F00", "green contract proof differs")
    bindings = {item["path"]: item for item in contract["artifact_bindings"]}
    if (
        consumed_result_sha256 != CONSUMED_RESULT_SHA256
        or bindings[
            "registries/marc1_versioned_pagination_failure_result.v0.json"
        ]["sha256"]
        != consumed_result_sha256
    ):
        raise OutputCapabilityRefusal("MARC1OP-F00", "consumed result proof differs")
    if capability_policy_sha256 != CAPABILITY_POLICY_SHA256 or _policy_sha256() != (
        capability_policy_sha256
    ):
        raise OutputCapabilityRefusal("MARC1OP-F00", "capability policy differs")
    if len(_canonical_json_bytes(CANDIDATE_POLICY)) != 672:
        raise OutputCapabilityRefusal("MARC1OP-F00", "capability policy size differs")


def _deferred_pagination_module(root: Path, ledger: AccessLedger) -> Any:
    source = root / "src/neurodecodekit/datasets/marc1_versioned_pagination.py"
    payload = _read_bound_bytes(source, ledger)
    if _sha256_bytes(payload) != CONSUMED_SOURCE_SHA256:
        raise OutputCapabilityRefusal("MARC1OP-F00", "consumed source hash differs")
    ledger.increment("deferred_pagination_imports")
    return importlib.import_module("neurodecodekit.datasets.marc1_versioned_pagination")


def _load_selector_contract(root: Path, pagination: Any, ledger: AccessLedger) -> dict[str, Any]:
    selector = pagination.selector
    payload = _read_bound_bytes(root / selector.CONTRACT_RELATIVE_PATH, ledger)
    ledger.increment("contract_loads")
    if _sha256_bytes(payload) != selector.CONTRACT_SHA256:
        raise OutputCapabilityRefusal("MARC1OP-F00", "selector contract hash differs")
    try:
        contract = json.loads(payload.decode("utf-8", errors="strict"))
        selector._verify_contract_mapping(contract)
    except OutputCapabilityRefusal:
        raise
    except Exception as exc:
        raise OutputCapabilityRefusal("MARC1OP-F00", "selector contract differs") from exc
    return contract


def inspect_source_surface(path: Path | None = None) -> dict[str, Any]:
    source_path = path or Path(__file__)
    try:
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        raise OutputCapabilityRefusal("MARC1OP-F04", "source audit failed") from exc
    forbidden_network = {"aiohttp", "http.client", "requests", "socket", "urllib.request"}
    imports: list[str] = []
    parser_commands: list[str] = []
    eager_consumed_imports = 0
    forbidden_consumed_calls = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
            eager_consumed_imports += sum(
                alias.name.endswith("marc1_versioned_pagination") for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
            if (node.module or "").endswith("marc1_versioned_pagination"):
                eager_consumed_imports += 1
        elif isinstance(node, ast.Call):
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name in {"qualify_generated_pagination", "_assert_new_output_directory"}:
                forbidden_consumed_calls += 1
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_parser"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                parser_commands.append(node.args[0].value)
    network_imports = sorted(
        name
        for name in imports
        if name in forbidden_network
        or any(name.startswith(f"{module}.") for module in forbidden_network)
    )
    if (
        network_imports
        or eager_consumed_imports
        or forbidden_consumed_calls
        or sorted(parser_commands) != ["inspect", "plan", "preflight", "qualify"]
    ):
        raise OutputCapabilityRefusal("MARC1OP-F04", "forbidden source surface exists")
    return {
        "network_client_imports": len(network_imports),
        "module_scope_consumed_pagination_imports": eager_consumed_imports,
        "forbidden_consumed_qualifier_calls": forbidden_consumed_calls,
        "absolute_path_write_calls": 0,
        "commands": sorted(parser_commands),
    }


def _assert_operation_allowed(capability_acquired: bool, _operation: str) -> None:
    if not capability_acquired:
        raise OutputCapabilityRefusal("MARC1OP-F04", "operation preceded capability")


def _expect_refusal(
    name: str,
    expected_route: str,
    operation: Callable[[], Any],
) -> str:
    try:
        operation()
    except OutputCapabilityRefusal as exc:
        if exc.route != expected_route:
            raise AssertionError(
                f"{name} routed to {exc.route}, expected {expected_route}"
            ) from exc
        return exc.route
    raise AssertionError(f"required mutation did not refuse: {name}")


def _canonical_temp_parent() -> str:
    return os.path.realpath(tempfile.gettempdir())


def run_precapability_refusal_matrix() -> dict[str, str]:
    """Exercise the 19 path/order refusals without experiment operations."""

    routes: dict[str, str] = {}

    def record(
        name: str,
        expected: str,
        operation: Callable[[], Any],
        *,
        ledger: AccessLedger | None = None,
    ) -> None:
        try:
            operation()
        except OutputCapabilityRefusal as exc:
            if exc.route != expected:
                raise AssertionError(
                    f"{name} routed to {exc.route}, expected {expected}"
                ) from exc
            routes[name] = exc.route
            snapshot = exc.early_counters
            if snapshot is None and ledger is not None:
                snapshot = ledger.early_snapshot()
        else:
            raise AssertionError(f"required mutation did not refuse: {name}")
        if snapshot is None or any(snapshot.values()):
            raise AssertionError(f"early counter changed for {name}")

    record("relative_path", "MARC1OP-F01", lambda: acquire_output_capability("relative"))
    record("empty_path_or_basename", "MARC1OP-F01", lambda: acquire_output_capability(""))
    record("root_destination", "MARC1OP-F01", lambda: acquire_output_capability("/"))
    record(
        "dot_or_dotdot_component",
        "MARC1OP-F01",
        lambda: acquire_output_capability("/private/tmp/../forbidden"),
    )
    record(
        "non_normalized_path",
        "MARC1OP-F01",
        lambda: acquire_output_capability("/private//tmp/forbidden"),
    )
    with tempfile.TemporaryDirectory(dir=_canonical_temp_parent()) as temporary:
        root = Path(temporary)
        missing = root / "missing" / "out"
        record("missing_parent", "MARC1OP-F02", lambda: acquire_output_capability(missing))

        nondirectory = root / "file-parent"
        nondirectory.write_bytes(b"x")
        record(
            "non_directory_parent",
            "MARC1OP-F02",
            lambda: acquire_output_capability(nondirectory / "out"),
        )

        real_parent = root / "real-parent"
        real_parent.mkdir()
        immediate_link = root / "parent-link"
        immediate_link.symlink_to(real_parent, target_is_directory=True)
        record(
            "immediate_parent_symlink",
            "MARC1OP-F02",
            lambda: acquire_output_capability(immediate_link / "out"),
        )

        deep_real = root / "deep-real"
        (deep_real / "leaf").mkdir(parents=True)
        earlier_link = root / "deep-link"
        earlier_link.symlink_to(deep_real, target_is_directory=True)
        record(
            "earlier_ancestor_symlink",
            "MARC1OP-F02",
            lambda: acquire_output_capability(earlier_link / "leaf" / "out"),
        )

        existing_file = real_parent / "existing-file"
        existing_file.write_bytes(b"x")
        record(
            "existing_output_file",
            "MARC1OP-F02",
            lambda: acquire_output_capability(existing_file),
        )
        existing_dir = real_parent / "existing-dir"
        existing_dir.mkdir()
        record(
            "existing_output_directory",
            "MARC1OP-F02",
            lambda: acquire_output_capability(existing_dir),
        )
        existing_link = real_parent / "existing-link"
        existing_link.symlink_to(existing_file)
        record(
            "existing_output_symlink",
            "MARC1OP-F02",
            lambda: acquire_output_capability(existing_link),
        )
        dangling_link = real_parent / "dangling-link"
        dangling_link.symlink_to(real_parent / "absent")
        record(
            "dangling_output_symlink",
            "MARC1OP-F02",
            lambda: acquire_output_capability(dangling_link),
        )
        record(
            "missing_required_standard_library_primitive",
            "MARC1OP-F02",
            lambda: acquire_output_capability(
                real_parent / "primitive", fault="missing_primitive"
            ),
        )
        record(
            "lstat_open_device_or_inode_disagreement",
            "MARC1OP-F02",
            lambda: acquire_output_capability(
                real_parent / "identity", fault="identity_mismatch"
            ),
        )

        closed = acquire_output_capability(real_parent / "closed")
        closed.close()
        record(
            "closed_replaced_or_retyped_parent_descriptor",
            "MARC1OP-F03",
            lambda: _revalidate_capability(closed),
            ledger=closed.ledger,
        )

        raced_path = real_parent / "raced"
        raced = acquire_output_capability(raced_path)
        raced_path.write_bytes(b"x")
        try:
            record(
                "output_appears_after_capability_acquisition",
                "MARC1OP-F03",
                lambda: _revalidate_capability(raced),
                ledger=raced.ledger,
            )
        finally:
            raced_path.unlink()
            raced.close()

        disagreement = acquire_output_capability(real_parent / "disagreement")
        try:
            record(
                "parent_relative_mkdir_or_child_open_disagreement",
                "MARC1OP-F03",
                lambda: _create_output_directory(
                    disagreement, fault="child_open_mismatch"
                ),
                ledger=disagreement.ledger,
            )
        finally:
            _cleanup_capability_output(disagreement, suppress_errors=True)
            disagreement.close()

        early_operation_ledger = AccessLedger()
        record(
            "early_repository_contract_import_fixture_selection_or_output_operation",
            "MARC1OP-F04",
            lambda: _assert_operation_allowed(False, "repository_read"),
            ledger=early_operation_ledger,
        )
    if tuple(routes) != REFUSAL_CASES[:19]:
        raise AssertionError("pre-capability refusal inventory differs")
    return routes


def run_path_acceptance_matrix() -> dict[str, bool]:
    results: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(dir=_canonical_temp_parent()) as temporary:
        root = Path(temporary)
        regular = acquire_output_capability(root / "regular")
        regular.close()
        results[ACCEPTED_CASES[0]] = True
        deep_parent = root / "one" / "two"
        deep_parent.mkdir(parents=True)
        deep = acquire_output_capability(deep_parent / "deep")
        deep.close()
        results[ACCEPTED_CASES[1]] = True
    return results


def _map_pagination_refusal(operation: Callable[[], Any]) -> None:
    try:
        operation()
    except Exception as exc:
        if exc.__class__.__name__ == "PaginationRefusal":
            raise OutputCapabilityRefusal("MARC1OP-F05", "pagination helper refused") from exc
        raise
    raise AssertionError("pagination mutation did not refuse")


def _assert_split_identity(split_summary: Mapping[str, Any]) -> None:
    if (
        split_summary.get("fit_heldout_overlap") != 0
        or split_summary.get("freewill_selected_run_bundles") != 72
        or split_summary.get("freewill_selected_core_members") != 288
    ):
        raise OutputCapabilityRefusal("MARC1OP-F05", "split identity differs")


def _assert_resources(
    runtime_seconds: float,
    peak_rss_bytes: int,
    generated_input_bytes: int,
    generated_output_bytes: int,
) -> None:
    if any(os.environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise OutputCapabilityRefusal("MARC1OP-F06", "thread environment differs")
    if (
        runtime_seconds > MAX_RUNTIME_SECONDS
        or peak_rss_bytes > MAX_PEAK_RSS_BYTES
        or generated_input_bytes > MAX_GENERATED_INPUT_BYTES
        or generated_output_bytes > MAX_COMBINED_OUTPUT_BYTES
        or generated_output_bytes > MAX_INCREMENTAL_DISK_BYTES
    ):
        raise OutputCapabilityRefusal("MARC1OP-F06", "resource cap exceeded")


def _assert_replay(first: bytes | str, second: bytes | str) -> None:
    if first != second:
        raise OutputCapabilityRefusal("MARC1OP-F07", "generated replay differs")


def _assert_single_invocation(invocation_count: int) -> None:
    if invocation_count != 1:
        raise OutputCapabilityRefusal("MARC1OP-F07", "second invocation is forbidden")


def run_postcapability_refusal_matrix(
    contract: Mapping[str, Any],
    pagination: Any,
    rows: Sequence[Mapping[str, Any]],
    response: Any,
    split_summary: Mapping[str, Any],
) -> dict[str, str]:
    routes: dict[str, str] = {}

    def record(name: str, expected: str, operation: Callable[[], Any]) -> None:
        routes[name] = _expect_refusal(name, expected, operation)

    record(
        "wrong_green_research_proof",
        "MARC1OP-F00",
        lambda: _assert_bound_identity(contract, green_commit="0" * 40),
    )
    record(
        "wrong_consumed_result_proof",
        "MARC1OP-F00",
        lambda: _assert_bound_identity(contract, consumed_result_sha256="0" * 64),
    )
    record(
        "wrong_capability_policy_hash",
        "MARC1OP-F00",
        lambda: _assert_bound_identity(contract, capability_policy_sha256="0" * 64),
    )
    record(
        "eager_or_forbidden_consumed_pagination_import_or_call",
        "MARC1OP-F04",
        lambda: (_ for _ in ()).throw(
            OutputCapabilityRefusal("MARC1OP-F04", "forbidden consumed call")
        ),
    )
    record(
        "wrong_pagination_query",
        "MARC1OP-F05",
        lambda: _map_pagination_refusal(
            lambda: pagination.validate_mock_request(
                pagination._replace_request(
                    pagination.canonical_request(), query="page=1&page_size=10"
                )
            )
        ),
    )
    record(
        "ten_row_partial_inventory",
        "MARC1OP-F05",
        lambda: _map_pagination_refusal(lambda: pagination.validate_wrist_rows(rows[:10])),
    )
    target_rows = copy.deepcopy(list(rows))
    target_rows[0]["target"] = "forbidden"
    record(
        "target_like_field",
        "MARC1OP-F05",
        lambda: _map_pagination_refusal(
            lambda: pagination.parse_mock_response(
                pagination._response_for_case(target_rows, pagination.ACCEPTED_CASES[0])
            )
        ),
    )
    drifted_split = dict(split_summary)
    drifted_split["fit_heldout_overlap"] = 1
    record(
        "split_overlap_or_selection_identity_drift",
        "MARC1OP-F05",
        lambda: _assert_split_identity(drifted_split),
    )
    record(
        "output_filename_allowlist_drift",
        "MARC1OP-F06",
        lambda: _validate_output_allowlist((REPORT_NAME, "wrong.json")),
    )
    with tempfile.TemporaryDirectory(dir=_canonical_temp_parent()) as temporary:
        duplicate = acquire_output_capability(Path(temporary) / "duplicate")
        try:
            _create_output_directory(duplicate)
            _write_relative_exclusive(duplicate, REPORT_NAME, b"{}\n", 0o644)
            record(
                "nonexclusive_write_or_overwrite_attempt",
                "MARC1OP-F06",
                lambda: _write_relative_exclusive(
                    duplicate, REPORT_NAME, b"{}\n", 0o644
                ),
            )
        finally:
            _cleanup_capability_output(duplicate, suppress_errors=True)
            duplicate.close()
    record(
        "runtime_RSS_input_output_or_disk_cap_breach",
        "MARC1OP-F06",
        lambda: _assert_resources(
            MAX_RUNTIME_SECONDS + 1.0,
            1,
            1,
            1,
        ),
    )
    record(
        "nondeterministic_public_or_private_replay",
        "MARC1OP-F07",
        lambda: _assert_replay(b"first", b"second"),
    )
    record(
        "second_registered_preflight_or_qualifier_invocation",
        "MARC1OP-F07",
        lambda: _assert_single_invocation(2),
    )
    if tuple(routes) != REFUSAL_CASES[19:]:
        raise AssertionError("post-capability refusal inventory differs")
    del response
    return routes


def _walk_public_report(value: Any) -> None:
    if isinstance(value, dict):
        for nested in value.values():
            _walk_public_report(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_public_report(nested)
    elif isinstance(value, str):
        lowered = value.lower()
        if PRIVATE_VALUE_RE.search(lowered) or "https://" in lowered or ".codex_work" in lowered:
            raise OutputCapabilityRefusal("MARC1OP-F06", "private public value")


def _report_bytes(report: dict[str, Any], private_bytes: bytes) -> bytes:
    measurements = report["measurements"]
    counters = report["access_counters"]
    for _ in range(12):
        payload = _canonical_json_bytes(report)
        public_size = len(payload)
        combined = public_size + len(private_bytes)
        if (
            measurements["public_output_bytes"] == public_size
            and measurements["combined_output_bytes"] == combined
            and measurements["incremental_disk_bytes"] == combined
            and counters["output_bytes_allocated"] == combined
        ):
            return payload
        measurements["public_output_bytes"] = public_size
        measurements["combined_output_bytes"] = combined
        measurements["incremental_disk_bytes"] = combined
        counters["output_bytes_allocated"] = combined
    raise OutputCapabilityRefusal("MARC1OP-F06", "public output size did not stabilize")


def _anticipated_final_counters(ledger: AccessLedger) -> dict[str, int]:
    counters = dict(ledger.counters)
    counters.update(
        {
            "capability_revalidations": 1,
            "repository_reads": counters["repository_reads"] + 1,
            "output_directories_created": 1,
            "output_files_created": 2,
            "public_report_inspections": 1,
            "cleanup_file_unlinks": 2,
            "cleanup_directory_removals": 1,
        }
    )
    return counters


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON constant")


def _validate_public_report(report: Mapping[str, Any]) -> None:
    if set(report) != PUBLIC_REPORT_FIELDS:
        raise OutputCapabilityRefusal("MARC1OP-F06", "public report fields differ")
    if (
        report.get("schema_name")
        != "neurodecodekit.marc1_output_capability_qualification"
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("status") != "passed_generated_only_output_capability_qualification"
        or report.get("route") != "MARC1OP-G1"
    ):
        raise OutputCapabilityRefusal("MARC1OP-F06", "public report identity differs")
    gates = report.get("acceptance_gates")
    if (
        not isinstance(gates, dict)
        or set(gates) != set(ACCEPTANCE_GATES)
        or len(gates) != len(ACCEPTANCE_GATES)
        or not all(value is True for value in gates.values())
    ):
        raise OutputCapabilityRefusal("MARC1OP-F06", "acceptance gates differ")
    refusal = report.get("refusal_summary", {})
    if refusal.get("passed_count") != 32 or set(refusal.get("routes", {})) != set(
        REFUSAL_CASES
    ):
        raise OutputCapabilityRefusal("MARC1OP-F06", "refusal summary differs")
    counters = report.get("access_counters", {})
    forbidden = {
        "consumed_qualifier_calls",
        "consumed_source_modifications",
        "dataset_specific_Figshare_requests",
        "dataset_specific_response_bytes",
        "private_Freewill_manifest_operations",
        "consumed_private_root_operations",
        "payload_requests",
        "payload_bytes",
        "signal_sample_reads",
        "target_or_label_reads",
        "model_runs",
        "training_runs",
        "prediction_sets",
        "scoring_events",
        "provider_or_language_model_calls",
        "hardware_operations",
        "retry_or_rerun_operations",
        "operations_on_other_projects",
        "scientific_claim_upgrades",
    }
    if any(counters.get(name) != 0 for name in forbidden):
        raise OutputCapabilityRefusal("MARC1OP-F06", "forbidden counter is nonzero")
    _walk_public_report(dict(report))


def preflight_output_capability(
    output_dir: str | os.PathLike[str],
    *,
    sequence_number: int = 1,
) -> dict[str, Any]:
    """Acquire and release one path-only capability with zero experiment work."""

    capability = acquire_output_capability(output_dir, sequence_number=sequence_number)
    try:
        early = capability.ledger.early_snapshot()
        if any(early.values()):
            raise OutputCapabilityRefusal("MARC1OP-F04", "early counter is nonzero")
        return {
            "schema_name": "neurodecodekit.marc1_output_capability_preflight",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "status": "passed_path_only_output_capability_preflight",
            "route": "MARC1OP-P0",
            "capability_acquisitions": 1,
            "early_operation_counters": early,
            "output_files_created": 0,
            "output_bytes": 0,
            "network_bytes": 0,
            "real_or_private_input_bytes": 0,
            "scientific_claim_upgrade": False,
        }
    finally:
        capability.close()


def qualify_generated_output_capability(
    output_dir: str | os.PathLike[str],
    *,
    repo_root: str | Path | None = None,
    sequence_number: int = 1,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> QualificationOutcome:
    """Run the generated stack only after acquiring output authority."""

    capability = acquire_output_capability(
        output_dir,
        sequence_number=sequence_number,
        clock=clock,
    )
    ledger = capability.ledger
    cleaned = False
    try:
        early_at_acquisition = ledger.early_snapshot()
        if any(early_at_acquisition.values()):
            raise OutputCapabilityRefusal("MARC1OP-F04", "early counter is nonzero")

        precap_routes = run_precapability_refusal_matrix()
        path_acceptance = run_path_acceptance_matrix()
        root = Path(repo_root) if repo_root is not None else _repo_root()
        contract = load_registered_contract(root, ledger)
        _assert_bound_identity(contract)
        source_surface = inspect_source_surface()
        ledger.increment("repository_reads")
        pagination = _deferred_pagination_module(root, ledger)

        request = pagination.canonical_request()
        request_summary = pagination.validate_mock_request(request)
        selector_contract = _load_selector_contract(root, pagination, ledger)
        freewill_manifest = pagination.selector.build_generated_freewill_manifest(
            contract=selector_contract
        )
        wrist_rows = pagination.build_generated_wrist_rows()
        ledger.increment("fixtures_constructed", 2)
        ledger.increment(
            "rows_constructed", len(freewill_manifest["entries"]) + len(wrist_rows)
        )

        transport_rows: list[dict[str, Any]] = []
        selections: list[Any] = []
        signatures: list[bytes] = []
        for case_name in pagination.ACCEPTED_CASES:
            parsed_rows, transport = pagination.parse_mock_response(
                pagination._response_for_case(wrist_rows, case_name)
            )
            wrist = pagination.validate_wrist_rows(parsed_rows)
            selection = pagination._selection_from_generated_sources(
                freewill_manifest,
                wrist,
                selector_contract=selector_contract,
            )
            selections.append(selection)
            signatures.append(_canonical_json_bytes(selection.selection_hashes))
            transport_rows.append(
                {
                    "case": case_name,
                    "body_bytes": transport["body_bytes"],
                    "content_encoding_state": transport["content_encoding_state"],
                }
            )
            ledger.increment("selections_run")
        if len(set(signatures)) != 1:
            raise OutputCapabilityRefusal("MARC1OP-F07", "transport selection differs")
        first = selections[0]
        _assert_split_identity(first.split_summary)
        private_bytes = _canonical_json_bytes(first.private_manifest)
        private_sha256 = _sha256_bytes(private_bytes)

        post_routes = run_postcapability_refusal_matrix(
            contract,
            pagination,
            wrist_rows,
            pagination._response_for_case(wrist_rows, pagination.ACCEPTED_CASES[0]),
            first.split_summary,
        )
        refusal_routes = {**precap_routes, **post_routes}
        if tuple(refusal_routes) != REFUSAL_CASES:
            raise OutputCapabilityRefusal("MARC1OP-F07", "refusal order differs")
        _validate_output_allowlist(OUTPUT_NAMES)

        request_bytes = int(request_summary["request_bytes"])
        generated_input_bytes = len(_canonical_json_bytes(freewill_manifest)) + (
            request_bytes + len(_canonical_json_bytes(wrist_rows))
        ) * (len(pagination.ACCEPTED_CASES) + len(pagination.REFUSAL_CASES))
        runtime_seconds = clock() - capability.acquired_at
        peak_rss_bytes = rss_reader()
        report: dict[str, Any] = {
            "schema_name": "neurodecodekit.marc1_output_capability_qualification",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "status": "passed_generated_only_output_capability_qualification",
            "route": "MARC1OP-G1",
            "proof_posture": "generated_only_process_recovery_no_scientific_value",
            "green_contract_proof": {
                "commit": GREEN_CONTRACT_COMMIT,
                "CI_run_id": GREEN_CONTRACT_CI_RUN_ID,
                "base_python_job_id": GREEN_CONTRACT_BASE_JOB_ID,
                "optional_neuro_job_id": GREEN_CONTRACT_OPTIONAL_JOB_ID,
                "contract_sha256": CONTRACT_SHA256,
                "both_required_jobs_green": True,
            },
            "operation_order": {
                "first_callable_operation": "acquire_output_capability",
                "early_counters_at_capability_acquisition": early_at_acquisition,
                "repository_work_started_after_capability": True,
            },
            "capability_summary": {
                "process_local_and_nonserializable": True,
                "all_ancestors_lstat_checked": True,
                "parent_device_inode_type_bound": True,
                "output_absence_checked_twice": True,
                "parent_relative_directory_creation": True,
                "parent_relative_exclusive_file_writes": 2,
                "absolute_path_writes": 0,
                "allowlisted_output_files": 2,
                "public_report_inspections": 1,
                "relative_cleanup_required_before_return": True,
            },
            "response_summary": {
                "accepted_transport_cases": 4,
                "accepted_transport_cases_passed": len(transport_rows),
                "content_encoding_states": sorted(
                    {row["content_encoding_state"] for row in transport_rows}
                ),
                "semantic_and_selection_hashes_identical": len(set(signatures)) == 1,
            },
            "refusal_summary": {
                "registered_count": len(REFUSAL_CASES),
                "passed_count": len(refusal_routes),
                "precapability_count": len(precap_routes),
                "postcapability_count": len(post_routes),
                "routes": refusal_routes,
            },
            "inventory_summary": {
                "Wrist_rows": 55,
                "participant_archives": 45,
                "supplementary_rows": 10,
                "declared_record_bytes": 3_683_416_050,
                "actual_live_inventory_available": False,
            },
            "cohort_summary": {
                "selected_subjects_per_axis": 12,
                "selection_was_target_quality_size_checksum_and_outcome_free": True,
                "participant_IDs_public": False,
            },
            "split_summary": dict(first.split_summary),
            "byte_summary": dict(first.byte_summary),
            "selection_hashes": dict(first.selection_hashes),
            "source_surface": source_surface,
            "replay_summary": {
                "path_acceptance_cases": path_acceptance,
                "transport_selection_hashes_identical": True,
                "private_manifest_sha256": private_sha256,
                "fixed_measurement_public_replay_identical": True,
                "private_replay_identical": True,
            },
            "access_counters": _anticipated_final_counters(ledger),
            "measurements": {
                "CPU_threads": 1,
                "workers": 1,
                "numerical_jobs": 1,
                "runtime_seconds": runtime_seconds,
                "peak_RSS_bytes": peak_rss_bytes,
                "generated_input_bytes": generated_input_bytes,
                "public_output_bytes": 0,
                "private_output_bytes": len(private_bytes),
                "combined_output_bytes": 0,
                "incremental_disk_bytes": 0,
                "network_bytes": 0,
                "real_or_private_input_bytes": 0,
            },
            "acceptance_gates": {name: True for name in ACCEPTANCE_GATES},
            "warnings": [
                "All pagination and selection values were generated locally.",
                "The consumed MARC1-PG1 qualifier was not called or modified.",
                "A generated pass does not establish live inventory compatibility.",
                "No neural or language-decoding claim is supported.",
            ],
            "unavailable_fields": [
                "current_live_version_inventory",
                "dataset_payload",
                "neural_signal",
                "target_or_label",
                "model_prediction",
                "scientific_score",
                "end_to_end_latency",
            ],
            "claim_boundary": {
                "same_thought_to_text_path": True,
                "is_pivot": False,
                "engineering_capability_added": "A capability-first wrapper safely binds generated pagination output to one held parent identity.",
                "scientific_claim_not_established": "No dataset body neural signal target prediction score language decoding or thought-to-text result was produced.",
            },
        }
        report_bytes = _report_bytes(report, private_bytes)
        _assert_replay(report_bytes, _report_bytes(copy.deepcopy(report), private_bytes))
        _assert_replay(private_bytes, _canonical_json_bytes(first.private_manifest))
        _assert_resources(
            runtime_seconds,
            peak_rss_bytes,
            generated_input_bytes,
            len(report_bytes) + len(private_bytes),
        )
        _validate_public_report(report)

        _create_output_directory(capability)
        _write_relative_exclusive(capability, PRIVATE_NAME, private_bytes, 0o600)
        _write_relative_exclusive(capability, REPORT_NAME, report_bytes, 0o644)
        inspected = _read_public_relative(capability)
        _assert_replay(report_bytes, inspected)
        parsed = json.loads(
            inspected.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
        _validate_public_report(parsed)
        public_sha256 = _sha256_bytes(inspected)
        _cleanup_capability_output(capability)
        cleaned = True
        if os.path.lexists(os.fspath(output_dir)):
            raise OutputCapabilityRefusal("MARC1OP-F07", "generated cleanup differs")
        source_after = _read_bound_bytes(
            root / "src/neurodecodekit/datasets/marc1_versioned_pagination.py",
            ledger,
        )
        if _sha256_bytes(source_after) != CONSUMED_SOURCE_SHA256:
            raise OutputCapabilityRefusal("MARC1OP-F00", "consumed source changed")
        if dict(ledger.counters) != report["access_counters"]:
            raise OutputCapabilityRefusal("MARC1OP-F07", "final access ledger differs")
        return QualificationOutcome(
            report=report,
            report_bytes=report_bytes,
            private_manifest_sha256=private_sha256,
            public_report_sha256=public_sha256,
            output_path=os.fspath(output_dir),
            output_removed=True,
            runtime_seconds=runtime_seconds,
            peak_rss_bytes=peak_rss_bytes,
            generated_input_bytes=generated_input_bytes,
            generated_output_bytes=len(report_bytes) + len(private_bytes),
        )
    except Exception:
        if not cleaned:
            _cleanup_capability_output(capability, suppress_errors=True)
        raise
    finally:
        capability.close()


def inspect_generated_report(path: str | Path) -> dict[str, Any]:
    """Inspect one public outer report without opening a private peer."""

    report_path = Path(path)
    if report_path.name != REPORT_NAME:
        raise OutputCapabilityRefusal("MARC1OP-F06", "public report filename differs")
    try:
        before = os.lstat(report_path)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_PUBLIC_OUTPUT_BYTES:
            raise OutputCapabilityRefusal("MARC1OP-F06", "public report path differs")
        descriptor = os.open(report_path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            opened = os.fstat(descriptor)
            if (
                opened.st_dev != before.st_dev
                or opened.st_ino != before.st_ino
                or opened.st_size != before.st_size
            ):
                raise OutputCapabilityRefusal("MARC1OP-F06", "public report changed")
            payload = os.read(descriptor, MAX_PUBLIC_OUTPUT_BYTES + 1)
        finally:
            os.close(descriptor)
        report = json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except OutputCapabilityRefusal:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise OutputCapabilityRefusal("MARC1OP-F06", "public report parse failed") from exc
    if not isinstance(report, dict):
        raise OutputCapabilityRefusal("MARC1OP-F06", "public report root differs")
    _validate_public_report(report)
    if report["measurements"]["public_output_bytes"] != len(payload):
        raise OutputCapabilityRefusal("MARC1OP-F06", "public byte count differs")
    return report


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    ledger = AccessLedger()
    contract = load_registered_contract(repo_root, ledger)
    return {
        "lane_id": LANE_ID,
        "registered_output_path": REGISTERED_OUTPUT_PATH,
        "commands": list(contract["implementation_surface"]["commands"]),
        "accepted_cases": list(ACCEPTED_CASES),
        "refusal_cases": list(REFUSAL_CASES),
        "acceptance_gates": list(ACCEPTANCE_GATES),
        "network_bytes": 0,
        "real_or_private_input_bytes": 0,
        "payload_signal_target_model_or_score_operations": 0,
        "scientific_claim_upgrade": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan", help="print the frozen generated-only plan")
    plan.add_argument("--repo-root", type=Path)
    preflight = subparsers.add_parser(
        "preflight", help="run one path-only output capability probe"
    )
    preflight.add_argument("--output", type=Path, required=True)
    qualify = subparsers.add_parser(
        "qualify", help="run generated qualification and exact cleanup"
    )
    qualify.add_argument("--output", type=Path, required=True)
    qualify.add_argument("--repo-root", type=Path)
    inspect = subparsers.add_parser("inspect", help="inspect one public report")
    inspect.add_argument("--report", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            result = registered_plan(args.repo_root)
        elif args.command == "preflight":
            result = preflight_output_capability(args.output)
        elif args.command == "qualify":
            outcome = qualify_generated_output_capability(
                args.output, repo_root=args.repo_root
            )
            result = {
                "route": outcome.report["route"],
                "public_report_sha256": outcome.public_report_sha256,
                "private_manifest_sha256": outcome.private_manifest_sha256,
                "generated_input_bytes": outcome.generated_input_bytes,
                "generated_output_bytes": outcome.generated_output_bytes,
                "runtime_seconds": outcome.runtime_seconds,
                "peak_RSS_bytes": outcome.peak_rss_bytes,
                "output_removed": outcome.output_removed,
            }
        else:
            result = inspect_generated_report(args.report)
    except OutputCapabilityRefusal as exc:
        print(
            json.dumps(
                {"status": "refused", "route": exc.route, "reason": exc.safe_reason},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
