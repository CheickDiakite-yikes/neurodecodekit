from __future__ import annotations

import ast
import copy
import dataclasses
import json
import stat
import tempfile
import unittest
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import cast

from neurodecodekit.datasets import fresh_motor_source_admission as admission

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_PROFILE_MODES = (
    ("OPENNEURO_CRN", "SOURCE_GLOBAL_REVISION"),
    ("NEMAR", "OPAQUE_COMPLETE_SNAPSHOT_REPLAY"),
    ("PHYSIONET", "SOURCE_GLOBAL_REVISION"),
    ("GIGADB", "OPAQUE_COMPLETE_SNAPSHOT_REPLAY"),
    ("BNCI_HORIZON_2020", "OPAQUE_COMPLETE_SNAPSHOT_REPLAY"),
)

EXPECTED_REFUSALS = (
    ("contract_digest_drift", "AUTHORITY_REFUSE"),
    ("unregistered_stage", "AUTHORITY_REFUSE"),
    ("saved_receipt_as_authority", "AUTHORITY_REFUSE"),
    ("incomplete_live_profile", "AUTHORITY_REFUSE"),
    ("captured_real_response_fixture", "AUTHORITY_REFUSE"),
    ("network_before_marker", "ORDER_REFUSE"),
    ("existing_consumed_marker", "ORDER_REFUSE"),
    ("marker_after_CI", "ORDER_REFUSE"),
    ("CI_W0_reused_as_CI_W1", "ORDER_REFUSE"),
    ("process_resume_from_receipt", "ORDER_REFUSE"),
    ("mutable_receipt_handoff", "ORDER_REFUSE"),
    ("source_contact_before_CI", "ORDER_REFUSE"),
    ("post_CI_process_exit_resume", "ORDER_REFUSE"),
    ("invalid_UTF8", "ENCODING_REFUSE"),
    ("UTF8_BOM", "ENCODING_REFUSE"),
    ("NUL_byte", "ENCODING_REFUSE"),
    ("trailing_JSON", "ENCODING_REFUSE"),
    ("nonfinite_number", "ENCODING_REFUSE"),
    ("depth_or_container_cap", "ENCODING_REFUSE"),
    ("duplicate_root_key", "DUPLICATE_REFUSE"),
    ("duplicate_nested_key", "DUPLICATE_REFUSE"),
    ("duplicate_index_id", "DUPLICATE_REFUSE"),
    ("duplicate_job_id", "DUPLICATE_REFUSE"),
    ("duplicate_singleton_header", "DUPLICATE_REFUSE"),
    ("unknown_authority_field", "SCHEMA_REFUSE"),
    ("missing_required_field", "SCHEMA_REFUSE"),
    ("boolean_numeric_identity", "SCHEMA_REFUSE"),
    ("float_numeric_identity", "SCHEMA_REFUSE"),
    ("confusable_enum_or_job_name", "SCHEMA_REFUSE"),
    ("mixed_mode_payload", "SCHEMA_REFUSE"),
    ("wrong_index_or_issuer", "IDENTITY_REFUSE"),
    ("wrong_request_profile_hash", "IDENTITY_REFUSE"),
    ("cross_source_evidence", "IDENTITY_REFUSE"),
    ("ledger_identity_drift", "IDENTITY_REFUSE"),
    ("weak_ETag_surrogate", "REVISION_REFUSE"),
    ("Last_Modified_surrogate", "REVISION_REFUSE"),
    ("body_hash_or_schema_surrogate", "REVISION_REFUSE"),
    ("partial_scope", "REVISION_REFUSE"),
    ("pre_post_revision_drift", "REVISION_REFUSE"),
    ("snapshot_page_gap", "SNAPSHOT_REFUSE"),
    ("snapshot_cycle_or_fork", "SNAPSHOT_REFUSE"),
    ("snapshot_reordered_body_hash", "SNAPSHOT_REFUSE"),
    ("snapshot_redirect_omission", "SNAPSHOT_REFUSE"),
    ("snapshot_pagination_conflict", "SNAPSHOT_REFUSE"),
    ("snapshot_early_terminal", "SNAPSHOT_REFUSE"),
    ("snapshot_terminal_with_next", "SNAPSHOT_REFUSE"),
    ("proxy_or_custom_CA_environment", "TRANSPORT_REFUSE"),
    ("custom_SSL_context_or_system_proxy", "TRANSPORT_REFUSE"),
    ("redirect_or_alternate_host_port", "TRANSPORT_REFUSE"),
    ("credential_cookie_or_conditional_request", "TRANSPORT_REFUSE"),
    ("nonglobal_or_postconnect_peer", "TRANSPORT_REFUSE"),
    ("cache_or_content_encoding", "TRANSPORT_REFUSE"),
    ("wrong_repository_or_owner_ID", "CI_RUN_REFUSE"),
    ("wrong_head_repository_or_owner_ID", "CI_RUN_REFUSE"),
    ("wrong_workflow_or_run_ID", "CI_RUN_REFUSE"),
    ("wrong_head_SHA", "CI_RUN_REFUSE"),
    ("wrong_event_or_branch", "CI_RUN_REFUSE"),
    ("wrong_attempt", "CI_RUN_REFUSE"),
    ("noncompleted_or_nonsuccess_run", "CI_RUN_REFUSE"),
    ("stale_Date_or_nonzero_Age", "CI_RUN_REFUSE"),
    ("wrong_API_media_or_version_profile", "CI_RUN_REFUSE"),
    ("job_total_count_or_pagination", "CI_JOB_REFUSE"),
    ("missing_required_job", "CI_JOB_REFUSE"),
    ("duplicate_required_job_name", "CI_JOB_REFUSE"),
    ("wrong_job_ID", "CI_JOB_REFUSE"),
    ("wrong_job_run_or_attempt", "CI_JOB_REFUSE"),
    ("wrong_job_head_SHA", "CI_JOB_REFUSE"),
    ("skipped_or_nonsuccess_job", "CI_JOB_REFUSE"),
    ("null_or_confusable_job_name", "CI_JOB_REFUSE"),
    ("request_count_cap", "RESOURCE_REFUSE"),
    ("wire_or_decoded_byte_cap", "RESOURCE_REFUSE"),
    ("runtime_or_RSS_cap", "RESOURCE_REFUSE"),
    ("generated_output_or_temp_disk_cap", "RESOURCE_REFUSE"),
    ("thread_worker_or_file_count_cap", "RESOURCE_REFUSE"),
    ("DNS_socket_TLS_HTTP_tripwire", "QUALIFICATION_NETWORK_REFUSE"),
    ("credential_environment_tripwire", "QUALIFICATION_NETWORK_REFUSE"),
    ("default_opener_or_network_import_tripwire", "QUALIFICATION_NETWORK_REFUSE"),
    ("marker_symlink_or_nonregular_parent", "ORDER_REFUSE"),
    ("marker_create_flags_or_permissions", "ORDER_REFUSE"),
    ("marker_file_fsync_failure", "ORDER_REFUSE"),
    ("marker_parent_fsync_failure", "ORDER_REFUSE"),
    ("marker_atomic_second_creator", "ORDER_REFUSE"),
)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _mutated_json(payload: bytes, mutate: Callable[[dict[str, object]], None]) -> bytes:
    value = cast(dict[str, object], admission.strict_json_loads(payload))
    mutate(value)
    return _canonical_bytes(value)


def _stabilize_report_size(report: dict[str, object]) -> dict[str, object]:
    measurements = cast(dict[str, object], report["measurements"])
    measurements["generated_output_bytes"] = 0
    for _ in range(8):
        size = len(admission.canonical_json_bytes(report))
        if measurements["generated_output_bytes"] == size:
            return report
        measurements["generated_output_bytes"] = size
    raise AssertionError("generated report byte count did not stabilize")


def _valid_public_report() -> dict[str, object]:
    report: dict[str, object] = {
        "schema_name": admission.SCHEMA_NAME,
        "schema_version": admission.SCHEMA_VERSION,
        "protocol_id": admission.PROTOCOL_ID,
        "status": "passed_generated_only_zero_network",
        "green_registration": {
            "commit": admission.GREEN_REGISTRATION_COMMIT,
            "CI_run_id": admission.GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": admission.GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_readers_job_id": admission.GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "qualification": {
            "deterministic_replays": 2,
            "replay_digest": "a" * 64,
            "replay_digests_equal": True,
            "profile_count_per_replay": 5,
            "global_revision_count_per_replay": 2,
            "snapshot_count_per_replay": 3,
            "CI_responses_per_replay": 2,
            "legal_ordering_sequences_per_replay": 1,
            "refusal_case_count": 82,
            "distinct_refusal_routes": 13,
            "all_refusals_passed": True,
            "refusals": [
                {
                    "mutation": name,
                    "expected_route": route,
                    "observed_route": route,
                    "status": "passed",
                }
                for name, route in EXPECTED_REFUSALS
            ],
        },
        "measurements": {
            "generated_input_bytes": 1,
            "generated_output_bytes": 0,
            "temporary_generated_bytes": 0,
            "temporary_generated_file_count": 0,
            "accepted_response_envelopes": 4,
            "marker_creates": 3,
            "marker_file_fsyncs": 3,
            "marker_directory_fsyncs": 5,
            "runtime_seconds": 0.1,
            "absolute_peak_RSS_bytes": 1,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "producer_is_causal": None,
            "end_to_end_latency_measured": False,
        },
        "operation_counters": {
            key: 0 for key in admission.OPERATION_COUNTER_KEYS
        },
        "warnings": list(admission.WARNINGS),
        "unavailable": list(admission.UNAVAILABLE_FIELDS),
        "claim_boundary": dict(admission.CLAIM_BOUNDARY),
    }
    return _stabilize_report_size(report)


class FreshMotorSourceAdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = admission.build_generated_fixture()

    @contextmanager
    def assert_refusal(self, route: str) -> Iterator[None]:
        with self.assertRaises(admission.FMSR1AdmissionRefusal) as caught:
            yield
        self.assertEqual(caught.exception.route, route)

    def test_registered_plan_is_generated_only_and_all_live_authority_is_closed(self) -> None:
        plan = admission.registered_plan(ROOT)
        self.assertEqual(plan["protocol_id"], "FMSR1-R1-G-v0")
        self.assertEqual(plan["named_refusal_mutations"], 82)
        self.assertEqual(plan["network_imports"], [])
        self.assertFalse(plan["live_command_present"])
        self.assertFalse(plan["network_or_real_source_authority"])
        self.assertFalse(plan["scientific_claim_authority"])

    def test_all_five_generated_revision_bundles_accept_in_frozen_modes(self) -> None:
        summary = admission.validate_revision_bundle(self.fixture["revision_bundle"])
        summaries = summary["profiles"]
        self.assertEqual(summary["profile_count"], 5)
        self.assertEqual(summary["global_revision_count"], 2)
        self.assertEqual(summary["snapshot_count"], 3)
        self.assertEqual(
            tuple((row["index_id"], row["mode"]) for row in summaries),
            EXPECTED_PROFILE_MODES,
        )

    def test_generated_revision_evidence_cannot_self_sign_changed_identity(self) -> None:
        bundle = copy.deepcopy(
            admission.strict_json_loads(self.fixture["revision_bundle"])
        )
        revision = bundle["profiles"][0]["source_global_revision"]
        revision["issuer_id"] = "ARBITRARY_GENERATED_ISSUER"
        with self.assert_refusal("IDENTITY_REFUSE"):
            admission.validate_revision_bundle(admission.canonical_json_bytes(bundle))

        bundle = copy.deepcopy(
            admission.strict_json_loads(self.fixture["revision_bundle"])
        )
        revision = bundle["profiles"][0]["source_global_revision"]
        revision["extraction_rule_sha256"] = "1" * 64
        with self.assert_refusal("REVISION_REFUSE"):
            admission.validate_revision_bundle(admission.canonical_json_bytes(bundle))

    def test_generated_snapshot_cannot_self_sign_changed_page_identity(self) -> None:
        bundle = copy.deepcopy(
            admission.strict_json_loads(self.fixture["revision_bundle"])
        )
        snapshot = bundle["profiles"][1]["opaque_complete_snapshot_replay"]
        snapshot["pages"][0]["response_body_sha256"] = "1" * 64
        snapshot["ledger_sha256"] = admission._sha256(
            admission.canonical_json_bytes(snapshot["pages"])
        )
        with self.assert_refusal("IDENTITY_REFUSE"):
            admission.validate_revision_bundle(admission.canonical_json_bytes(bundle))

    def test_snapshot_poison_candidate_is_never_interpreted(self) -> None:
        payload = self.fixture["revision_bundle"]
        self.assertNotIn(b"POISON-CANDIDATE", payload)
        summary = admission.validate_revision_bundle(payload)
        snapshots = [
            row
            for row in summary["profiles"]
            if row["mode"] == "OPAQUE_COMPLETE_SNAPSHOT_REPLAY"
        ]
        self.assertEqual(len(snapshots), 3)
        for snapshot in snapshots:
            self.assertEqual(
                set(snapshot),
                {"index_id", "mode", "page_count", "ledger_sha256"},
            )

    def test_attempt_specific_generated_CI_evidence_accepts(self) -> None:
        summary = admission.validate_github_ci_evidence(
            self.fixture["ci_profile"],
            self.fixture["run_response"],
            self.fixture["jobs_response"],
            environ={},
        )
        self.assertEqual(summary["run_attempt"], 1)
        self.assertEqual(
            [row["name"] for row in summary["required_jobs"]],
            ["Base Python", "Optional Neuro Readers"],
        )
        self.assertEqual(summary["response_count"], 2)

    def test_generated_CI_profile_and_response_provenance_are_fixed(self) -> None:
        profile = copy.deepcopy(self.fixture["ci_profile"])
        profile["api_version"] = "arbitrary-version"
        with self.assert_refusal("CI_RUN_REFUSE"):
            admission.validate_github_ci_evidence(
                profile,
                self.fixture["run_response"],
                self.fixture["jobs_response"],
                environ={},
            )

        captured = dataclasses.replace(
            self.fixture["run_response"], provenance="CAPTURED_REAL_RESPONSE"
        )
        with self.assert_refusal("AUTHORITY_REFUSE"):
            admission.validate_github_ci_evidence(
                self.fixture["ci_profile"],
                captured,
                self.fixture["jobs_response"],
                environ={},
            )

        changed_peer = dataclasses.replace(
            self.fixture["run_response"], postconnect_peer_unchanged=False
        )
        with self.assert_refusal("TRANSPORT_REFUSE"):
            admission.validate_github_ci_evidence(
                self.fixture["ci_profile"],
                changed_peer,
                self.fixture["jobs_response"],
                environ={},
            )

    def test_generated_authority_profile_is_exact_and_activation_is_separate(self) -> None:
        summary = admission.validate_generated_authority_profile(
            self.fixture["authority_profile"]
        )
        self.assertFalse(summary["network_authority"])
        changed = copy.deepcopy(self.fixture["authority_profile"])
        changed["saved_receipt_authority"] = True
        with self.assert_refusal("AUTHORITY_REFUSE"):
            admission.validate_generated_authority_profile(changed)
        with tempfile.TemporaryDirectory() as directory, self.assert_refusal(
            "AUTHORITY_REFUSE"
        ):
            admission._load_implementation_activation(Path(directory))

    def test_strict_JSON_accepts_integers_and_rejects_ambiguity(self) -> None:
        self.assertEqual(admission.strict_json_loads(b'{"a":1,"nested":{"b":2}}'), {
            "a": 1,
            "nested": {"b": 2},
        })

        cases = (
            (b'{"a":1,"a":2}', "DUPLICATE_REFUSE", "duplicate_root_key"),
            (
                b'{"outer":{"a":1,"a":2}}',
                "DUPLICATE_REFUSE",
                "duplicate_nested_key",
            ),
            (b'{"a":1.25}', "ENCODING_REFUSE", "float_numeric_identity"),
            (b'\xef\xbb\xbf{"a":1}', "ENCODING_REFUSE", "UTF8_BOM"),
            (b'{"a":1} trailing', "ENCODING_REFUSE", "trailing_JSON"),
            (b'{"a":NaN}', "ENCODING_REFUSE", "nonfinite_number"),
            (b'{"a":"x\x00y"}', "ENCODING_REFUSE", "NUL_byte"),
        )
        for payload, route, mutation in cases:
            with self.subTest(mutation=mutation), self.assert_refusal(route):
                admission.strict_json_loads(payload)

    def test_CI_run_identity_mutations_refuse(self) -> None:
        run_response = self.fixture["run_response"]
        cases = (
            (
                "wrong_repository_or_owner_ID",
                lambda value: value["repository"].__setitem__(
                    "id", value["repository"]["id"] + 1
                ),
            ),
            (
                "wrong_workflow_or_run_ID",
                lambda value: value.__setitem__("workflow_id", value["workflow_id"] + 1),
            ),
            (
                "wrong_head_SHA",
                lambda value: value.__setitem__("head_sha", "0" * 40),
            ),
            (
                "wrong_attempt",
                lambda value: value.__setitem__("run_attempt", 2),
            ),
        )
        for mutation, mutate in cases:
            changed = _mutated_json(run_response.body, mutate)
            headers = tuple(
                (name, str(len(changed)) if name.casefold() == "content-length" else value)
                for name, value in run_response.headers
            )
            response = dataclasses.replace(run_response, body=changed, headers=headers)
            with self.subTest(mutation=mutation), self.assert_refusal("CI_RUN_REFUSE"):
                admission.validate_github_ci_evidence(
                    self.fixture["ci_profile"],
                    response,
                    self.fixture["jobs_response"],
                    environ={},
                )

    def test_CI_job_identity_and_success_mutations_refuse(self) -> None:
        jobs_response = self.fixture["jobs_response"]

        def wrong_job_id(value: dict[str, object]) -> None:
            value["jobs"][0]["id"] += 1

        def duplicate_job_name(value: dict[str, object]) -> None:
            value["jobs"][1]["name"] = value["jobs"][0]["name"]

        def skipped_job(value: dict[str, object]) -> None:
            value["jobs"][0]["status"] = "completed"
            value["jobs"][0]["conclusion"] = "skipped"

        cases = (
            ("wrong_job_ID", wrong_job_id),
            ("duplicate_required_job_name", duplicate_job_name),
            ("skipped_or_nonsuccess_job", skipped_job),
        )
        for mutation, mutate in cases:
            changed = _mutated_json(jobs_response.body, mutate)
            headers = tuple(
                (name, str(len(changed)) if name.casefold() == "content-length" else value)
                for name, value in jobs_response.headers
            )
            response = dataclasses.replace(jobs_response, body=changed, headers=headers)
            with self.subTest(mutation=mutation), self.assert_refusal("CI_JOB_REFUSE"):
                admission.validate_github_ci_evidence(
                    self.fixture["ci_profile"],
                    self.fixture["run_response"],
                    response,
                    environ={},
                )

    def test_execution_order_accepts_only_marker_then_CI_then_source_contact(self) -> None:
        legal = ("marker_durable", "CI_W0_success", "source_contact_started")
        summary = admission.validate_execution_order(legal)
        self.assertEqual(tuple(summary["events"]), legal)
        self.assertTrue(summary["same_process"])
        self.assertFalse(summary["receipt_authority"])

        cases = (
            (("CI_W0_success", "marker_durable"), "marker_after_CI"),
            (
                ("marker_durable", "source_contact_started", "CI_W0_success"),
                "source_contact_before_CI",
            ),
            (
                ("marker_durable", "CI_W0_success", "CI_W1_success"),
                "CI_W0_reused_as_CI_W1",
            ),
        )
        for events, mutation in cases:
            with self.subTest(mutation=mutation), self.assert_refusal("ORDER_REFUSE"):
                admission.validate_execution_order(events)

    def test_consumed_marker_is_exclusive_no_follow_and_mode_0600(self) -> None:
        with admission._qualification_temp_root("fmsr1-test-marker-") as parent:
            summary = admission.create_consumed_marker(
                parent, self.fixture["marker_bytes"], expected_stage="CI_W0"
            )
            marker = parent / summary["marker_name"]
            self.assertEqual(marker.read_bytes(), self.fixture["marker_bytes"])
            self.assertEqual(stat.S_IMODE(marker.stat().st_mode), 0o600)
            with self.assert_refusal("ORDER_REFUSE"):
                admission.create_consumed_marker(
                    parent, self.fixture["marker_bytes"], expected_stage="CI_W0"
                )

    def test_consumed_marker_rejects_unowned_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assert_refusal("ORDER_REFUSE"):
                admission.create_consumed_marker(
                    Path(directory),
                    self.fixture["marker_bytes"],
                    expected_stage="CI_W0",
                )

    def test_consumed_marker_rejects_wrong_identity_before_creation(self) -> None:
        cases = (
            ("protocol_id", "WRONG_PROTOCOL"),
            ("stage", "OFFICIAL_GENERATED_QUALIFICATION"),
            ("execution_ordinal", 2),
            ("generated", False),
        )
        for field, changed_value in cases:
            with self.subTest(field=field), admission._qualification_temp_root(
                "fmsr1-test-marker-identity-"
            ) as parent:
                marker = copy.deepcopy(
                    admission.strict_json_loads(self.fixture["marker_bytes"])
                )
                marker[field] = changed_value
                with self.assert_refusal("ORDER_REFUSE"):
                    admission.create_consumed_marker(
                        parent,
                        admission.canonical_json_bytes(marker),
                        expected_stage="CI_W0",
                    )
                self.assertFalse((parent / "consumed.json").exists())

    def test_official_generated_root_is_durable_and_one_shot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo_root = Path(directory)
            with admission._official_qualification_root(repo_root) as (
                attempt_root,
                marker,
            ):
                self.assertEqual(marker["mode"], "0600")
                self.assertEqual(marker["attempt_state"], "armed_and_consumed")
                self.assertEqual(marker["ancestry_directory_fsyncs"], 2)
                self.assertEqual(marker["directory_fsyncs"], 3)
                self.assertTrue((attempt_root / "consumed.json").is_file())
            self.assertTrue((attempt_root / "consumed.json").is_file())
            with self.assert_refusal("ORDER_REFUSE"):
                with admission._official_qualification_root(repo_root):
                    pass

    def test_consumed_marker_rejects_symlink_or_non_directory_parent(self) -> None:
        with admission._qualification_temp_root("fmsr1-test-parent-") as root:
            real_parent = root / "real"
            real_parent.mkdir()
            linked_parent = root / "linked"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            with self.assert_refusal("ORDER_REFUSE"):
                admission.create_consumed_marker(
                    linked_parent,
                    self.fixture["marker_bytes"],
                    expected_stage="CI_W0",
                )

            file_parent = root / "not-a-directory"
            file_parent.write_bytes(b"generated")
            with self.assert_refusal("ORDER_REFUSE"):
                admission.create_consumed_marker(
                    file_parent,
                    self.fixture["marker_bytes"],
                    expected_stage="CI_W0",
                )

    def test_marker_fsync_faults_leave_the_attempt_consumed(self) -> None:
        def fail_fsync(_fd: int) -> None:
            raise OSError("generated fsync fault")

        cases = (("file_fsync", fail_fsync, None), ("parent_fsync", None, fail_fsync))
        for fault_at, file_fsync, directory_fsync in cases:
            with self.subTest(fault_at=fault_at), admission._qualification_temp_root(
                "fmsr1-test-fsync-"
            ) as parent:
                kwargs: dict[str, object] = {}
                if file_fsync is not None:
                    kwargs["file_fsync"] = file_fsync
                if directory_fsync is not None:
                    kwargs["directory_fsync"] = directory_fsync
                with self.assert_refusal("ORDER_REFUSE"):
                    admission.create_consumed_marker(
                        parent,
                        self.fixture["marker_bytes"],
                        expected_stage="CI_W0",
                        **kwargs,
                    )
                self.assertEqual(len(tuple(parent.iterdir())), 1)
                with self.assert_refusal("ORDER_REFUSE"):
                    admission.create_consumed_marker(
                        parent,
                        self.fixture["marker_bytes"],
                        expected_stage="CI_W0",
                    )

    def test_public_report_accepts_fixture_and_rejects_authority_or_resource_drift(self) -> None:
        report = _valid_public_report()
        self.assertIsNone(admission.validate_public_report(report))

        mutations: list[Mapping[str, object]] = []
        network = copy.deepcopy(report)
        network["operation_counters"]["network_requests"] = 1
        mutations.append(network)
        claim = copy.deepcopy(report)
        claim["claim_boundary"]["scientific_claim_not_established"] = "changed"
        mutations.append(claim)
        runtime = copy.deepcopy(report)
        runtime["measurements"]["runtime_seconds"] = 31
        mutations.append(runtime)
        refusal = copy.deepcopy(report)
        refusal["qualification"]["refusals"].pop()
        mutations.append(refusal)
        nested_leak = copy.deepcopy(report)
        nested_leak["qualification"]["notes"] = {"opaque": "private material"}
        mutations.append(nested_leak)
        oversized = copy.deepcopy(report)
        oversized["warnings"].append("x" * (1024**2))
        mutations.append(oversized)

        for mutation in mutations:
            _stabilize_report_size(cast(dict[str, object], mutation))
            with self.subTest(keys=tuple(mutation)), self.assertRaises(
                admission.FMSR1AdmissionRefusal
            ):
                admission.validate_public_report(mutation)

    def test_refusal_matrix_has_exact_frozen_names_routes_and_order(self) -> None:
        matrix = admission.run_refusal_matrix(ROOT)
        rows = matrix["cases"]
        observed = tuple(
            (row["mutation"], row["observed_route"])
            for row in rows
        )
        self.assertTrue(matrix["all_passed"])
        self.assertEqual(matrix["case_count"], 82)
        self.assertEqual(len(observed), 82)
        self.assertEqual(len({name for name, _route in observed}), 82)
        self.assertEqual(observed, EXPECTED_REFUSALS)

    def test_component_helpers_never_run_the_official_qualification(self) -> None:
        original = admission.run_generated_qualification

        def forbidden(*_args: object, **_kwargs: object) -> object:
            raise AssertionError("official qualification must not run in component tests")

        admission.run_generated_qualification = forbidden
        try:
            admission.registered_plan(ROOT)
            admission.build_generated_fixture()
        finally:
            admission.run_generated_qualification = original

    def test_admission_module_has_no_network_or_dynamic_import_surface(self) -> None:
        module_path = (
            ROOT / "src/neurodecodekit/datasets/fresh_motor_source_admission.py"
        )
        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
        self.assertTrue(
            imported_roots.isdisjoint(
                {
                    "aiohttp",
                    "github",
                    "http",
                    "httpx",
                    "requests",
                    "socket",
                    "ssl",
                    "urllib",
                }
            ),
            imported_roots,
        )
        for forbidden in ("__import__(", "import_module(", "urlopen(", "create_connection("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
