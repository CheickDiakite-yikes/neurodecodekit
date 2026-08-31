from __future__ import annotations

import copy
import hashlib
import http.client
import inspect
import io
import os
import stat
import tempfile
import time
import unittest
from collections.abc import Callable, Mapping
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import fresh_motor_source_identity_witness as core
from neurodecodekit.datasets import fresh_motor_source_identity_witness_live as live


ROOT = Path(__file__).resolve().parents[1]
POISON = "REFERENCE_TARGET_DO_NOT_RETAIN_LIVE"


def _artifact(payload: bytes = b"live-adapter") -> dict[str, object]:
    return {
        "path": "src/neurodecodekit/datasets/fresh_motor_source_identity_witness_live.py",
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "git_blob": live._git_blob(payload),
    }


def _record_identity(payload: bytes = b"live-implementation-record") -> dict[str, object]:
    return {
        "path": live.LIVE_IMPLEMENTATION_RECORD_RELATIVE_PATH.as_posix(),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "git_blob": live._git_blob(payload),
    }


def _CI_profile() -> dict[str, object]:
    return live.canonical_CI_W0_profile()


def _valid_decision() -> dict[str, object]:
    artifact = _artifact()
    artifacts = [artifact]
    artifact_set_sha256 = hashlib.sha256(core.canonical_json_bytes(artifacts)).hexdigest()
    CI_profile = _CI_profile()
    return {
        "schema_name": ("neurodecodekit.fresh_motor_source_identity_witness_execution_decision"),
        "schema_version": live.SCHEMA_VERSION,
        "decision_id": live.EXECUTION_DECISION_ID,
        "packet_id": live.PACKET_ID,
        "recorded_at": "2026-08-31",
        "status": live.EXECUTION_DECISION_STATUS,
        "maintainer_words": "continue exact FMSR1 live witness",
        "maintainer_words_utf8_bytes": len(b"continue exact FMSR1 live witness"),
        "maintainer_words_sha256": hashlib.sha256(b"continue exact FMSR1 live witness").hexdigest(),
        "packet_artifacts": [dict(row) for row in live.PACKET_ARTIFACTS],
        "effective_only_after_decision_commit_pushed_and_both_CI_jobs_green": True,
        "repository_identity": {
            "numeric_repository_id": live.REPOSITORY_ID,
            "numeric_owner_id": live.OWNER_ID,
            "numeric_head_repository_id": live.REPOSITORY_ID,
            "numeric_head_owner_id": live.OWNER_ID,
        },
        "workflow_identity": {
            "path": live.WORKFLOW_PATH,
            "bytes": live.WORKFLOW_BYTES,
            "sha256": live.WORKFLOW_SHA256,
            "git_blob": live.WORKFLOW_BLOB_SHA1,
        },
        "green_live_implementation": {
            "commit": "b" * 40,
            "CI_run_id": 1,
            "base_python_job_id": 2,
            "base_python_job_conclusion": "success",
            "optional_neuro_readers_job_id": 3,
            "optional_neuro_readers_job_conclusion": "success",
            "both_required_jobs_green": True,
            "on_GitHub_main": True,
            "implementation_record": _record_identity(),
            "artifacts": artifacts,
            "artifact_count": len(artifacts),
            "artifact_set_sha256": artifact_set_sha256,
        },
        "CI_W0_profile": {
            "canonical_profile": CI_profile,
            "canonical_profile_sha256": hashlib.sha256(
                core.canonical_json_bytes(CI_profile, newline=True)
            ).hexdigest(),
        },
        "authorization_after_decision_green": {
            "one_consumed_same_process_live_witness": True,
            "three_request_CI_W0": True,
            "five_profile_seventeen_root_source_witness": True,
            "opaque_candidate_byte_count_and_hash_only": True,
            "candidate_semantic_parsing_ranking_or_selection": False,
            "payload_header_signal_event_annotation_target_or_label": False,
            "model_checkpoint_training_inference_prediction_or_score": False,
            "language_model_provider_stream_device_or_hardware": False,
            "release_or_scientific_claim_upgrade": False,
            "retry_rerun_resume_repair_substitute_or_post_result_amend": False,
            "touch_other_project_or_delete_existing_path": False,
        },
        "decision_only_operation_counters": dict(live.EXECUTION_DECISION_OPERATION_COUNTERS),
        "next_barriers": dict(live.EXECUTION_NEXT_BARRIERS),
        "claim_boundary": dict(core.CLAIM_BOUNDARY),
    }


def _authority(head: str = "a" * 40) -> live.ExecutionAuthority:
    decision = _valid_decision()
    payload = core.canonical_json_bytes(decision, newline=True)
    implementation = decision["green_live_implementation"]
    CI_profile = decision["CI_W0_profile"]
    assert isinstance(implementation, Mapping)
    assert isinstance(CI_profile, Mapping)
    return live.ExecutionAuthority(
        decision=decision,
        decision_payload=payload,
        decision_sha256=hashlib.sha256(payload).hexdigest(),
        decision_git_blob=live._git_blob(payload),
        local_HEAD=head,
        implementation_commit=str(implementation["commit"]),
        implementation_artifact_set_sha256=str(implementation["artifact_set_sha256"]),
        CI_W0_profile_sha256=str(CI_profile["canonical_profile_sha256"]),
    )


def _CI_receipt(authority: live.ExecutionAuthority) -> dict[str, object]:
    digest = hashlib.sha256(b"generated-CI-receipt-field").hexdigest()
    return {
        "local_HEAD_authority_commit": authority.local_HEAD,
        "authority_decision_blob_sha256": digest,
        "current_main_ref_request_identity_sha256": digest,
        "current_main_ref_response_sha256": digest,
        "exact_check_runs_request_identity_sha256": digest,
        "Base_Python_check_run_id": 101,
        "Optional_Neuro_Readers_check_run_id": 102,
        "check_runs_response_sha256": digest,
        "workflow_blob_request_identity_sha256": digest,
        "workflow_blob_response_sha256": digest,
    }


def _contact_result(
    body: bytes,
    *,
    media_type: str = "application/json",
    status: int = 200,
    headers: tuple[tuple[str, str], ...] | None = None,
) -> live.ContactResult:
    active_headers = headers or (
        ("Content-Type", f"{media_type}; charset=utf-8"),
        ("Content-Encoding", "identity"),
        ("Content-Length", str(len(body))),
    )
    header_digest = hashlib.sha256(
        core.canonical_json_bytes([list(row) for row in active_headers])
    ).hexdigest()
    peer_digest = hashlib.sha256(b"203.0.113.10").hexdigest()
    return live.ContactResult(
        status=status,
        headers=active_headers,
        body=body,
        DNS_answer_set_sha256=hashlib.sha256(b"generated-dns").hexdigest(),
        selected_peer_sha256=peer_digest,
        post_connect_peer_sha256=peer_digest,
        selected_and_post_connect_peer_equal_and_global=True,
        TLS_version="TLSv1.3",
        response_headers_sha256=header_digest,
        content_encoding="identity",
        transfer_framing="content_length",
        wire_body_bytes=len(body),
        request_elapsed_nanoseconds=1_000,
        whole_invocation_elapsed_nanoseconds=2_000,
    )


def _openneuro_response(cursor: str | None, has_next: bool) -> bytes:
    return core.canonical_json_bytes(
        {
            "data": {
                "datasets": {
                    "edges": [{"node": {"id": POISON, "name": POISON}}],
                    "pageInfo": {
                        "endCursor": cursor,
                        "hasNextPage": has_next,
                    },
                }
            }
        }
    )


def _source_contact(
    *,
    root_zero_bodies: tuple[bytes, ...] | None = None,
    exchange_overrides: Mapping[str, core.FixtureExchange] | None = None,
) -> tuple[live.ContactCallable, list[live.PreparedRequest]]:
    packet = core.load_packet(ROOT)
    roots = core.build_root_plan(ROOT)
    fixture = core.build_generated_fixture(ROOT)
    exchanges = fixture["exchanges"]
    assert isinstance(exchanges, list)
    by_identity: dict[str, core.FixtureExchange] = {
        exchange.request_identity_sha256: exchange for exchange in exchanges
    }

    if root_zero_bodies is not None:
        root = roots[0]
        current_url = root.url
        current_body = root.body
        for response_body in root_zero_bodies:
            identity, _headers = core.request_identity(
                packet, root, url=current_url, body=current_body
            )
            headers = (
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Encoding", "identity"),
                ("Content-Length", str(len(response_body))),
            )
            by_identity[identity] = core.FixtureExchange(
                identity,
                "application/json",
                response_body,
                headers,
            )
            next_url, next_body, _control = core._parse_control(
                packet,
                root,
                current_url,
                current_body,
                "application/json",
                response_body,
            )
            if next_url is None or next_body is None:
                break
            current_url, current_body = next_url, next_body
    if exchange_overrides is not None:
        by_identity.update(exchange_overrides)

    calls: list[live.PreparedRequest] = []

    def contact(
        request: live.PreparedRequest,
        _ordinal: int,
        _deadline: float,
        _started: float,
    ) -> live.ContactResult:
        if request.kind != "SOURCE":
            raise AssertionError("generated source contact received non-source request")
        calls.append(request)
        try:
            exchange = by_identity[request.request_identity_sha256]
        except KeyError as exc:
            raise AssertionError("unregistered generated request identity") from exc
        return _contact_result(
            exchange.response_body,
            media_type=exchange.media_type,
            headers=exchange.response_headers,
        )

    return contact, calls


class FreshMotorSourceIdentityWitnessLiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.network_patches = (
            mock.patch("socket.getaddrinfo", side_effect=AssertionError("network closed")),
            mock.patch("socket.socket", side_effect=AssertionError("network closed")),
            mock.patch.object(live, "_peak_rss_bytes", return_value=1),
        )
        for patcher in self.network_patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def assert_live_refusal(
        self,
        operation: Callable[[], object],
        code: str = "LIVE_AUTHORITY_REFUSE",
    ) -> None:
        with self.assertRaises(live.LiveWitnessRefusal) as raised:
            operation()
        self.assertEqual(raised.exception.code, code)

    def assert_park(
        self,
        operation: Callable[[], object],
        route: str,
        reason: str | None = None,
    ) -> None:
        with self.assertRaises(live.LiveWitnessPark) as raised:
            operation()
        self.assertEqual(raised.exception.route, route)
        if reason is not None:
            self.assertEqual(raised.exception.reason_class, reason)

    def test_registered_plan_is_exact_bounded_and_nonclaiming(self) -> None:
        plan = live.registered_live_plan()
        self.assertEqual(plan["packet_id"], live.PACKET_ID)
        self.assertEqual(plan["implementation_id"], live.LIVE_IMPLEMENTATION_ID)
        self.assertEqual(plan["execution_decision_id"], live.EXECUTION_DECISION_ID)
        self.assertTrue(plan["execution_decision_required"])
        self.assertEqual(plan["official_index_profiles"], 5)
        self.assertEqual(plan["root_request_count"], 17)
        self.assertEqual(plan["CI_request_count"], 3)
        self.assertEqual(plan["maximum_official_index_requests"], 125)
        self.assertEqual(plan["maximum_total_network_requests"], 128)
        self.assertEqual(plan["commands"], ["plan", "qualify-generated", "execute"])
        self.assertEqual(plan["generated_qualification_network_requests"], 0)
        self.assertEqual(
            plan["CI_W0_profile_sha256"],
            hashlib.sha256(core.canonical_json_bytes(_CI_profile(), newline=True)).hexdigest(),
        )
        self.assertEqual(plan["candidate_semantic_operations"], 0)
        self.assertEqual(plan["payload_or_neural_reads"], 0)
        self.assertEqual(plan["model_or_score_operations"], 0)
        self.assertFalse(plan["scientific_claim_established"])
        self.assertEqual(
            tuple(inspect.signature(live.execute_registered_witness).parameters),
            (),
        )

    def test_execution_decision_accepts_only_the_bound_authority(self) -> None:
        live.validate_execution_decision(_valid_decision())

        mutations: list[tuple[str, dict[str, object]]] = []
        for name, path, value in (
            ("schema", ("schema_version",), "9.9.9"),
            ("packet", ("packet_id",), "OTHER"),
            (
                "repository",
                ("repository_identity", "numeric_repository_id"),
                0,
            ),
            ("workflow", ("workflow_identity", "sha256"), "0" * 64),
            (
                "green",
                ("green_live_implementation", "both_required_jobs_green"),
                False,
            ),
            (
                "artifact_count",
                ("green_live_implementation", "artifact_count"),
                2,
            ),
            (
                "artifact_digest",
                ("green_live_implementation", "artifact_set_sha256"),
                "0" * 64,
            ),
            (
                "implementation_record",
                (
                    "green_live_implementation",
                    "implementation_record",
                    "path",
                ),
                "registries/other.json",
            ),
            (
                "CI_profile",
                ("CI_W0_profile", "canonical_profile_sha256"),
                "0" * 64,
            ),
            (
                "true_authority",
                (
                    "authorization_after_decision_green",
                    "one_consumed_same_process_live_witness",
                ),
                False,
            ),
            (
                "false_authority",
                (
                    "authorization_after_decision_green",
                    "payload_header_signal_event_annotation_target_or_label",
                ),
                True,
            ),
            (
                "decision_counter",
                ("decision_only_operation_counters", "network_requests"),
                1,
            ),
            (
                "claim_boundary",
                ("claim_boundary", "scientific_claim_established"),
                True,
            ),
        ):
            mutated = copy.deepcopy(_valid_decision())
            target: dict[str, object] = mutated
            for key in path[:-1]:
                child = target[key]
                assert isinstance(child, dict)
                target = child
            target[path[-1]] = value
            mutations.append((name, mutated))

        bad_path = copy.deepcopy(_valid_decision())
        implementation = bad_path["green_live_implementation"]
        assert isinstance(implementation, dict)
        artifacts = implementation["artifacts"]
        assert isinstance(artifacts, list)
        assert isinstance(artifacts[0], dict)
        artifacts[0]["path"] = "../escape.py"
        mutations.append(("artifact_path", bad_path))

        extra_root = copy.deepcopy(_valid_decision())
        extra_root["future_execution_commit"] = "c" * 40
        mutations.append(("extra_root_field", extra_root))

        for name, mutated in mutations:
            with self.subTest(name=name):
                self.assert_live_refusal(
                    lambda mutated=mutated: live.validate_execution_decision(mutated)
                )

    def test_local_git_proof_is_system_bound_config_closed_and_allowlisted(self) -> None:
        completed = mock.Mock(stdout="proof\n")
        with mock.patch.object(live.subprocess, "run", return_value=completed) as run:
            self.assertEqual(live._git(ROOT, "rev-parse", "HEAD"), "proof\n")
        command = run.call_args.args[0]
        options = run.call_args.kwargs
        self.assertEqual(command[0], "/usr/bin/git")
        for key, value in live.HERMETIC_GIT_CONFIG:
            self.assertIn(f"{key}={value}", command)
        self.assertEqual(command[-2:], ["rev-parse", "HEAD"])
        self.assertEqual(options["env"]["GIT_CONFIG_NOSYSTEM"], "1")
        self.assertEqual(options["env"]["GIT_CONFIG_GLOBAL"], os.devnull)
        self.assertEqual(options["env"]["GIT_NO_LAZY_FETCH"], "1")
        self.assertEqual(options["env"]["GIT_TERMINAL_PROMPT"], "0")
        self.assertEqual(options["env"]["PATH"], "/usr/bin:/bin")
        self.assertIs(options["stdin"], live.subprocess.DEVNULL)
        self.assertTrue(options["close_fds"])

        with mock.patch.object(live.subprocess, "run") as forbidden:
            self.assert_live_refusal(
                lambda: live._git(ROOT, "fetch", "origin"),
                "LIVE_AUTHORITY_REFUSE",
            )
        forbidden.assert_not_called()

    def test_request_and_byte_caps_fail_closed_before_overrun(self) -> None:
        budget = live.RequestBudget(started=time.monotonic())
        for _ in range(live.MAX_CI_REQUESTS):
            budget.claim("CI")
        self.assert_park(lambda: budget.claim("CI"), "WITNESS_CAP_PARK", "CI_REQUEST_CAP")

        budget = live.RequestBudget(started=time.monotonic())
        for _ in range(live.MAX_SOURCE_REQUESTS):
            budget.claim("SOURCE")
        self.assert_park(
            lambda: budget.claim("SOURCE"),
            "WITNESS_CAP_PARK",
            "SOURCE_REQUEST_CAP",
        )

        budget = live.RequestBudget(started=time.monotonic())
        for _ in range(live.MAX_CI_REQUESTS):
            budget.claim("CI")
        for _ in range(live.MAX_SOURCE_REQUESTS):
            budget.claim("SOURCE")
        self.assert_park(
            lambda: budget.claim("SOURCE"),
            "WITNESS_CAP_PARK",
            "TOTAL_REQUEST_CAP",
        )

        CI_budget = live.RequestBudget(started=time.monotonic())
        CI_budget.add_body("CI", live.MAX_CI_BYTES, live.MAX_CI_BYTES)
        self.assert_park(
            lambda: CI_budget.add_body("CI", 1, 1),
            "WITNESS_CAP_PARK",
            "CI_BYTE_CAP",
        )
        source_budget = live.RequestBudget(started=time.monotonic())
        source_budget.add_body(
            "SOURCE",
            live.MAX_SOURCE_WIRE_BYTES,
            live.MAX_SOURCE_ENTITY_BYTES,
        )
        self.assert_park(
            lambda: source_budget.add_body("SOURCE", 1, 1),
            "WITNESS_CAP_PARK",
            "SOURCE_BYTE_CAP",
        )
        self.assert_live_refusal(
            lambda: live.RequestBudget(started=time.monotonic()).add_body("CI", -1, -1),
            "LIVE_RESOURCE_REFUSE",
        )
        valid_threads = {key: "1" for key in live.THREAD_ENV_KEYS}
        self.assert_live_refusal(
            lambda: live._validate_environment({**valid_threads, "GIT_DIR": "/tmp/alternate-git"}),
            "LIVE_ENVIRONMENT_REFUSE",
        )

        packet = core.load_packet(ROOT)
        root = core.build_root_plan(ROOT)[0]
        request = live._source_request(packet, root, root.url, root.body)
        bounded_budget = live.RequestBudget(started=time.monotonic())
        bounded_budget.source_wire_bytes = live.MAX_SOURCE_WIRE_BYTES - 4
        bounded_budget.source_entity_bytes = live.MAX_SOURCE_ENTITY_BYTES - 4

        def cap_plus_one_contact(
            bounded: live.PreparedRequest,
            _ordinal: int,
            _deadline: float,
            _started: float,
        ) -> live.ContactResult:
            self.assertEqual(bounded.maximum_response_bytes, 4)
            return _contact_result(b"12345")

        high_RSS_contact = mock.Mock(side_effect=AssertionError("contact must stay closed"))
        with mock.patch.object(
            live, "_peak_rss_bytes", return_value=live.MAX_PEAK_RSS_BYTES + 1
        ):
            self.assert_park(
                lambda: live._contact_once(
                    request,
                    budget=live.RequestBudget(started=time.monotonic()),
                    contact=high_RSS_contact,
                    deadline=time.monotonic() + 1,
                ),
                "WITNESS_CAP_PARK",
                "PEAK_RSS_CAP",
            )
        high_RSS_contact.assert_not_called()

        self.assert_park(
            lambda: live._contact_once(
                request,
                budget=bounded_budget,
                contact=cap_plus_one_contact,
                deadline=time.monotonic() + 1,
            ),
            "WITNESS_CAP_PARK",
            "PAGE_BYTE_CAP",
        )
        self.assertEqual(bounded_budget.source_requests, 1)

    def test_attempt_root_and_marker_are_durable_private_and_one_shot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reservation = live.reserve_consumed_attempt(root, _authority())
            attempt_root = reservation.attempt_root
            marker_payload = reservation.marker_payload
            marker_path = attempt_root / live.CONSUMED_MARKER_NAME
            self.assertEqual(stat.S_IMODE(os.lstat(attempt_root).st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(os.lstat(marker_path).st_mode), 0o600)
            self.assertEqual(marker_path.read_bytes(), marker_payload)
            live.verify_consumed_marker(reservation)
            replaced = live.AttemptReservation(
                attempt_root=reservation.attempt_root,
                marker_payload=reservation.marker_payload,
                attempt_device=reservation.attempt_device,
                attempt_inode=reservation.attempt_inode + 1,
            )
            self.assert_live_refusal(
                lambda: live.verify_consumed_marker(replaced),
                "LIVE_PATH_REFUSE",
            )
            marker = core.strict_json_loads(marker_payload)
            self.assertEqual(marker["state"], "ARMED_CONSUMED")
            self.assertEqual(marker["execution_decision_id"], live.EXECUTION_DECISION_ID)
            self.assertEqual(marker["packet_id"], live.PACKET_ID)
            self.assert_live_refusal(
                lambda: live.reserve_consumed_attempt(root, _authority()),
                "LIVE_PATH_REFUSE",
            )
            self.assertEqual(marker_path.read_bytes(), marker_payload)

    def test_CI_W0_uses_exactly_three_injected_calls_and_validates_all_proofs(self) -> None:
        fixture = core.build_generated_CI_fixture(ROOT)
        main_ref = core.strict_json_loads(fixture["main_ref"])
        check_runs = core.strict_json_loads(fixture["check_runs"])
        assert isinstance(main_ref, dict)
        assert isinstance(check_runs, dict)
        rows = check_runs.get("check_runs")
        assert isinstance(rows, list)
        repository = {
            "id": live.REPOSITORY_ID,
            "owner": {"id": live.OWNER_ID},
        }
        for row in rows:
            assert isinstance(row, dict)
            row["repository"] = copy.deepcopy(repository)
            row["head_repository"] = copy.deepcopy(repository)
        main_ref["ref"] = "refs/heads/main"
        responses = (
            _contact_result(core.canonical_json_bytes(main_ref)),
            _contact_result(core.canonical_json_bytes(check_runs)),
            _contact_result(fixture["workflow_blob"]),
        )
        calls: list[live.PreparedRequest] = []

        def contact(
            request: live.PreparedRequest,
            ordinal: int,
            _deadline: float,
            _started: float,
        ) -> live.ContactResult:
            calls.append(request)
            return responses[ordinal]

        budget = live.RequestBudget(started=time.monotonic())
        receipt = live.run_CI_W0(
            _authority(fixture["head"].decode("ascii")),
            budget=budget,
            contact=contact,
            deadline=time.monotonic() + 5,
        )
        self.assertEqual(len(calls), 3)
        self.assertEqual(
            [request.url for request in calls],
            [
                f"https://{live.CI_HOST}{live.CI_MAIN_PATH}",
                f"https://{live.CI_HOST}{live.CI_CHECKS_TEMPLATE.format(head='a' * 40)}",
                f"https://{live.CI_HOST}{live.CI_WORKFLOW_PATH}",
            ],
        )
        self.assertTrue(all(request.kind == "CI" for request in calls))
        self.assertEqual(budget.CI_requests, 3)
        self.assertEqual(budget.source_requests, 0)
        self.assertEqual(receipt["Base_Python_check_run_id"], 101)
        self.assertEqual(receipt["Optional_Neuro_Readers_check_run_id"], 102)

        wrapped_blob = core.strict_json_loads(fixture["workflow_blob"])
        assert isinstance(wrapped_blob, dict)
        content = wrapped_blob["content"]
        assert isinstance(content, str)
        wrapped_blob["content"] = "\n".join(
            content[offset : offset + 76] for offset in range(0, len(content), 76)
        )
        wrapped_responses = (
            responses[0],
            responses[1],
            _contact_result(core.canonical_json_bytes(wrapped_blob)),
        )

        def wrapped_contact(
            _request: live.PreparedRequest,
            ordinal: int,
            _deadline: float,
            _started: float,
        ) -> live.ContactResult:
            return wrapped_responses[ordinal]

        wrapped_receipt = live.run_CI_W0(
            _authority(fixture["head"].decode("ascii")),
            budget=live.RequestBudget(started=time.monotonic()),
            contact=wrapped_contact,
            deadline=time.monotonic() + 5,
        )
        self.assertEqual(wrapped_receipt["Base_Python_check_run_id"], 101)

        missing_repository = copy.deepcopy(check_runs)
        missing_rows = missing_repository["check_runs"]
        assert isinstance(missing_rows, list)
        assert isinstance(missing_rows[0], dict)
        missing_rows[0].pop("head_repository")
        missing_responses = (
            responses[0],
            _contact_result(core.canonical_json_bytes(missing_repository)),
            responses[2],
        )

        def missing_repository_contact(
            _request: live.PreparedRequest,
            ordinal: int,
            _deadline: float,
            _started: float,
        ) -> live.ContactResult:
            return missing_responses[ordinal]

        self.assert_park(
            lambda: live.run_CI_W0(
                _authority(fixture["head"].decode("ascii")),
                budget=live.RequestBudget(started=time.monotonic()),
                contact=missing_repository_contact,
                deadline=time.monotonic() + 5,
            ),
            "WITNESS_TRANSPORT_PARK",
            "CI_REPOSITORY_IDENTITY",
        )

        bad_checks = core.strict_json_loads(fixture["check_runs"])
        assert isinstance(bad_checks, dict)
        bad_checks["total_count"] = 3
        bad_responses = (
            responses[0],
            _contact_result(core.canonical_json_bytes(bad_checks)),
            responses[2],
        )

        def bad_contact(
            _request: live.PreparedRequest,
            ordinal: int,
            _deadline: float,
            _started: float,
        ) -> live.ContactResult:
            return bad_responses[ordinal]

        self.assert_park(
            lambda: live.run_CI_W0(
                _authority(fixture["head"].decode("ascii")),
                budget=live.RequestBudget(started=time.monotonic()),
                contact=bad_contact,
                deadline=time.monotonic() + 5,
            ),
            "WITNESS_TRANSPORT_PARK",
            "CI_CHECK_CARDINALITY",
        )

    def test_interim_HTTP_and_query_changing_redirects_park(self) -> None:
        class FakeSocket:
            def makefile(self, _mode: str, buffering: int | None = None) -> io.BytesIO:
                del buffering
                return io.BytesIO(
                    b"HTTP/1.1 100 Continue\r\n\r\nHTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"
                )

        response = live._NoInterimHTTPResponse(FakeSocket(), method="GET")  # type: ignore[arg-type]
        with self.assertRaises(http.client.HTTPException):
            response.begin()

        packet = core.load_packet(ROOT)
        root = next(row for row in core.build_root_plan(ROOT) if "?" in row.url)
        separator = "&" if "?" in root.url else "?"
        self.assert_park(
            lambda: live._canonical_redirect_url(
                packet,
                root,
                root.url,
                f"{root.url}{separator}page=999",
            ),
            "WITNESS_TRANSPORT_PARK",
            "REDIRECT_ALLOWLIST",
        )

    def test_framing_cap_plus_one_and_expired_deadline_park(self) -> None:
        self.assert_park(
            lambda: live._response_framing(
                {
                    "content-length": ["1"],
                    "transfer-encoding": ["chunked"],
                }
            ),
            "WITNESS_TRANSPORT_PARK",
            "CONFLICTING_RESPONSE_FRAMING",
        )

        class CapPlusOneBody:
            def read(self, maximum: int) -> bytes:
                self.maximum = maximum
                return b"x" * maximum

        body = CapPlusOneBody()
        self.assert_park(
            lambda: live._read_response_body(  # type: ignore[arg-type]
                body,
                8,
                None,
            ),
            "WITNESS_CAP_PARK",
            "PAGE_BYTE_CAP",
        )
        self.assertEqual(body.maximum, 9)
        self.assert_park(
            lambda: live._remaining_timeout(time.monotonic() - 1.0),
            "WITNESS_CAP_PARK",
            "RUNTIME_CAP",
        )
        with mock.patch.object(
            live.socket,
            "getaddrinfo",
            side_effect=live._DNSDeadlineExpired,
        ):
            self.assert_park(
                lambda: live._bounded_getaddrinfo("example.com", time.monotonic() + 1.0),
                "WITNESS_CAP_PARK",
                "RUNTIME_CAP",
            )

    def test_variable_length_traversal_hashes_three_page_root_without_poison(self) -> None:
        contact, calls = _source_contact(
            root_zero_bodies=(
                _openneuro_response("cursor-live-a", True),
                _openneuro_response("cursor-live-b", True),
                _openneuro_response(None, False),
            )
        )
        budget = live.RequestBudget(started=time.monotonic())
        audit = live.SemanticAccessAudit()
        ledger = live.build_live_ledger(
            ROOT,
            budget=budget,
            contact=contact,
            deadline=time.monotonic() + 15,
            audit=audit,
        )
        first_root = ledger["profiles"][0]["roots"][0]
        self.assertEqual(first_root["page_count"], 3)
        self.assertEqual(ledger["total_page_count"], 35)
        self.assertEqual(len(calls), 35)
        self.assertEqual(budget.source_requests, 35)
        self.assertEqual(budget.CI_requests, 0)
        public_ledger = core.canonical_json_bytes(ledger, newline=True)
        self.assertNotIn(POISON.encode("ascii"), public_ledger)
        self.assertNotIn(b"reference_text", public_ledger)
        self.assertNotIn(b'"target"', public_ledger)
        self.assertGreater(ledger["total_entity_body_bytes"], 0)
        self.assertEqual(audit.candidate_semantic_accesses, 0)
        self.assertGreater(audit.control_fields_accessed, 0)
        self.assertGreater(audit.opaque_members_skipped, 0)

        budget.CI_requests = 3
        budget.CI_bytes = 3
        budget.total_requests += 3
        authority = _authority()
        result = live._base_result(
            authority,
            budget,
            route="WITNESS_COMPLETE",
            started=time.monotonic(),
            state_transcript=live.STATE_MACHINE,
        )
        result.update(
            {
                "profile_count": len(ledger["profiles"]),
                "root_count": ledger["total_root_count"],
                "page_count": ledger["total_page_count"],
                "global_ledger_sha256": ledger["canonical_global_ledger_sha256"],
                "source_index_snapshot_identity_established": True,
                "consumed_marker_bytes": 123,
                "CI_W0_receipt": _CI_receipt(authority),
            }
        )
        rendered, result_payload, ledger_payload = live._render_result_artifacts(
            result, ledger, marker_bytes=123
        )
        public_output = result_payload + ledger_payload
        self.assertNotIn(POISON.encode("ascii"), public_output)
        self.assertEqual(rendered["result_artifact_bytes"], len(result_payload))
        self.assertEqual(rendered["ledger_artifact_bytes"], len(ledger_payload))
        self.assertEqual(
            rendered["retained_artifact_bytes"],
            len(result_payload) + len(ledger_payload) + 123,
        )
        self.assertEqual(
            result_payload,
            core.canonical_json_bytes(rendered, newline=True),
        )

    def test_HTML_candidate_links_and_ignored_templates_are_not_control_access(self) -> None:
        audit = live.SemanticAccessAudit()
        poison = "REFERENCE_TARGET_DO_NOT_RETAIN_candidate_link"
        payload = (
            '<html><body><a class="candidate" href="'
            + poison
            + '">candidate</a><template><nav aria-label="pagination">'
            '<a rel="next" href="'
            + poison
            + '">ignored</a></nav></template><nav aria-label="pagination">'
            '<a rel="candidate" href="' + poison + '">candidate inside control container</a>'
            '<a rel="next" aria-disabled="true">next</a></nav></body></html>'
        ).encode()
        reference, control = live._extract_selective_generic_HTML_control(payload, audit)
        self.assertIsNone(reference)
        self.assertEqual(control, {"variant": "HTML_TERMINAL", "terminal": True})
        self.assertEqual(audit.candidate_semantic_accesses, 0)
        self.assertGreater(audit.control_fields_accessed, 0)
        self.assertGreater(audit.opaque_members_skipped, 0)

    def test_pagination_cycle_cap_and_malformed_control_park(self) -> None:
        packet = core.load_packet(ROOT)
        roots = core.build_root_plan(ROOT)
        cycle_root = roots[4]
        cycle_url = core._next_url(cycle_root)
        cycle_body = core.canonical_json_bytes(
            {"items": [{"reference_text": POISON}], "next": cycle_url}
        )
        cycle_headers = (
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Encoding", "identity"),
            ("Content-Length", str(len(cycle_body))),
        )
        initial_identity = core.request_identity(packet, cycle_root)[0]
        cycle_identity = core.request_identity(packet, cycle_root, url=cycle_url, body=b"")[0]
        cycle_contact, _calls = _source_contact(
            exchange_overrides={
                identity: core.FixtureExchange(
                    identity,
                    "application/json",
                    cycle_body,
                    cycle_headers,
                )
                for identity in (initial_identity, cycle_identity)
            }
        )
        self.assert_park(
            lambda: live.build_live_ledger(
                ROOT,
                budget=live.RequestBudget(started=time.monotonic()),
                contact=cycle_contact,
                deadline=time.monotonic() + 10,
            ),
            "WITNESS_TRANSPORT_PARK",
            "PAGINATION_CYCLE",
        )

        normal_contact, _calls = _source_contact()
        with mock.patch.object(live, "MAX_SOURCE_REQUESTS", 1):
            self.assert_park(
                lambda: live.build_live_ledger(
                    ROOT,
                    budget=live.RequestBudget(started=time.monotonic()),
                    contact=normal_contact,
                    deadline=time.monotonic() + 10,
                ),
                "WITNESS_CAP_PARK",
                "SOURCE_REQUEST_CAP",
            )

        root = roots[0]
        bad_body = b'{"data":{"datasets":{"pageInfo":{"hasNextPage":true,"endCursor":null}}}}'
        initial_identity = core.request_identity(packet, root)[0]

        def malformed_contact(
            request: live.PreparedRequest,
            _ordinal: int,
            _deadline: float,
            _started: float,
        ) -> live.ContactResult:
            self.assertEqual(request.request_identity_sha256, initial_identity)
            return _contact_result(bad_body)

        self.assert_park(
            lambda: live.build_live_ledger(
                ROOT,
                budget=live.RequestBudget(started=time.monotonic()),
                contact=malformed_contact,
                deadline=time.monotonic() + 10,
            ),
            "WITNESS_TRANSPORT_PARK",
            "PAGINATION_REFUSE",
        )

    def test_park_result_byte_accounting_converges_without_ledger(self) -> None:
        budget = live.RequestBudget(started=time.monotonic())
        result = live._base_result(
            _authority(),
            budget,
            route="WITNESS_CAP_PARK",
            started=time.monotonic(),
            state_transcript=(
                "CLOSED",
                "LOCAL_PREFLIGHT",
                "FINALIZE",
                "COMPLETE_OR_PARK",
            ),
        )
        result["park_reason_class"] = "GENERATED_CAP"
        result["consumed_marker_bytes"] = 123
        result["CI_W0_receipt"] = None
        rendered, result_payload, ledger_payload = live._render_result_artifacts(
            result, None, marker_bytes=123
        )
        self.assertEqual(ledger_payload, b"")
        self.assertEqual(rendered["ledger_artifact_bytes"], 0)
        self.assertEqual(rendered["temporary_artifact_bytes"], 0)
        self.assertEqual(rendered["result_artifact_bytes"], len(result_payload))
        self.assertEqual(rendered["retained_artifact_bytes"], len(result_payload) + 123)
        self.assertLessEqual(len(result_payload), live.MAX_RETAINED_BYTES)
        self.assertEqual(
            result_payload,
            core.canonical_json_bytes(rendered, newline=True),
        )


if __name__ == "__main__":
    unittest.main()
