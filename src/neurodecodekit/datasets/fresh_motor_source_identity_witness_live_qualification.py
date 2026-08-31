"""Generated-only qualification for the FMSR1 execution-locked live adapter."""

from __future__ import annotations

import copy
import hashlib
import io
import os
import tempfile
import time
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, replace
from email.utils import formatdate
from pathlib import Path
from unittest import mock
from urllib.parse import urlsplit, urlunsplit

from neurodecodekit.datasets import fresh_motor_source_identity_witness as core
from neurodecodekit.datasets import fresh_motor_source_identity_witness_live as live


QUALIFICATION_ID = "FMSR1-R1-W-I1-Q0"
QUALIFICATION_CONSUMED = True
MAX_QUALIFICATION_SECONDS = 30.0
MAX_GENERATED_INPUT_BYTES = 4 * 1024**2
MAX_QUALIFICATION_REPORT_BYTES = 1024**2
POISON_PREFIX = b"REFERENCE_TARGET_DO_NOT_RETAIN_"
GENERATED_MONOTONIC_START = 1_000.0
GENERATED_WALL_TIME = 1_800_000_000.0


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _artifact(path: str, payload: bytes) -> dict[str, object]:
    return {
        "path": path,
        "bytes": len(payload),
        "sha256": _sha256(payload),
        "git_blob": live._git_blob(payload),
    }


def load_green_live_implementation_decision(repo_root: str | Path) -> Mapping[str, object]:
    root = Path(repo_root).resolve()
    payload = live._read_regular_nofollow(
        root / live.LIVE_IMPLEMENTATION_DECISION_RELATIVE_PATH,
        live.LIVE_IMPLEMENTATION_DECISION_BYTES,
    )
    if (
        len(payload) != live.LIVE_IMPLEMENTATION_DECISION_BYTES
        or _sha256(payload) != live.LIVE_IMPLEMENTATION_DECISION_SHA256
        or live._git_blob(payload) != live.LIVE_IMPLEMENTATION_DECISION_GIT_BLOB
    ):
        raise live.LiveWitnessRefusal(
            "LIVE_AUTHORITY_REFUSE", "live implementation decision drifted"
        )
    decision = live._strict_mapping(payload)
    proof = decision.get("green_generated_implementation_proof")
    authority = decision.get("authorization_after_decision_green")
    if (
        decision.get("decision_id") != live.LIVE_IMPLEMENTATION_DECISION_ID
        or decision.get("packet_id") != live.PACKET_ID
        or decision.get("effective_only_after_decision_commit_pushed_and_both_CI_jobs_green")
        is not True
        or not isinstance(proof, Mapping)
        or proof.get("commit") != "ea37358d8f34efd70f4e95c2a8452aa727f1b2bd"
        or proof.get("CI_run_id") != 33_361_847_146
        or proof.get("base_python_job_id") != 99_394_572_164
        or proof.get("optional_neuro_readers_job_id") != 99_394_572_060
        or proof.get("both_required_jobs_green") is not True
        or proof.get("on_GitHub_main") is not True
        or not isinstance(authority, Mapping)
        or authority.get("additive_standard_library_live_executor") is not True
        or authority.get("generated_qualification_once") is not True
        or authority.get("GitHub_API_or_official_index_contact") is not False
        or authority.get("live_source_identity_witness") is not False
        or authority.get("release_or_scientific_claim_upgrade") is not False
    ):
        raise live.LiveWitnessRefusal(
            "LIVE_AUTHORITY_REFUSE", "green implementation authority differs"
        )
    return decision


def _CI_profile() -> dict[str, object]:
    return live.canonical_CI_W0_profile()


def build_generated_execution_decision() -> dict[str, object]:
    artifacts = [
        _artifact(
            "src/neurodecodekit/datasets/fresh_motor_source_identity_witness_live.py",
            b"generated-live-adapter-artifact",
        )
    ]
    CI_profile = _CI_profile()
    words = "generated fixture authority only"
    return {
        "schema_name": ("neurodecodekit.fresh_motor_source_identity_witness_execution_decision"),
        "schema_version": live.SCHEMA_VERSION,
        "decision_id": live.EXECUTION_DECISION_ID,
        "packet_id": live.PACKET_ID,
        "recorded_at": "2026-08-31",
        "status": live.EXECUTION_DECISION_STATUS,
        "maintainer_words": words,
        "maintainer_words_utf8_bytes": len(words.encode("utf-8")),
        "maintainer_words_sha256": _sha256(words.encode("utf-8")),
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
            "CI_run_id": 101,
            "base_python_job_id": 102,
            "base_python_job_conclusion": "success",
            "optional_neuro_readers_job_id": 103,
            "optional_neuro_readers_job_conclusion": "success",
            "both_required_jobs_green": True,
            "on_GitHub_main": True,
            "implementation_record": _artifact(
                live.LIVE_IMPLEMENTATION_RECORD_RELATIVE_PATH.as_posix(),
                b"generated-live-implementation-record",
            ),
            "artifacts": artifacts,
            "artifact_count": len(artifacts),
            "artifact_set_sha256": _sha256(core.canonical_json_bytes(artifacts)),
        },
        "CI_W0_profile": {
            "canonical_profile": CI_profile,
            "canonical_profile_sha256": _sha256(
                core.canonical_json_bytes(CI_profile, newline=True)
            ),
        },
        "authorization_after_decision_green": dict(live.EXECUTION_AUTHORITY),
        "decision_only_operation_counters": dict(live.EXECUTION_DECISION_OPERATION_COUNTERS),
        "next_barriers": dict(live.EXECUTION_NEXT_BARRIERS),
        "claim_boundary": dict(core.CLAIM_BOUNDARY),
    }


def _generated_authority(head: str) -> live.ExecutionAuthority:
    decision = build_generated_execution_decision()
    live.validate_execution_decision(decision)
    payload = core.canonical_json_bytes(decision, newline=True)
    implementation = decision["green_live_implementation"]
    CI_profile = decision["CI_W0_profile"]
    assert isinstance(implementation, Mapping)
    assert isinstance(CI_profile, Mapping)
    return live.ExecutionAuthority(
        decision=decision,
        decision_payload=payload,
        decision_sha256=_sha256(payload),
        decision_git_blob=live._git_blob(payload),
        local_HEAD=head,
        implementation_commit=str(implementation["commit"]),
        implementation_artifact_set_sha256=str(implementation["artifact_set_sha256"]),
        CI_W0_profile_sha256=str(CI_profile["canonical_profile_sha256"]),
    )


def _HTTP_response(
    status: int,
    headers: list[tuple[str, str]],
    body: bytes,
    *,
    chunked: bool = False,
) -> bytes:
    active = [
        (name, value)
        for name, value in headers
        if name.casefold() not in {"content-length", "transfer-encoding", "date"}
    ]
    active.append(("Date", formatdate(time.time(), usegmt=True)))
    if chunked:
        active.append(("Transfer-Encoding", "chunked"))
        framed = f"{len(body):X}\r\n".encode("ascii") + body + b"\r\n0\r\n\r\n"
    else:
        active.append(("Content-Length", str(len(body))))
        framed = body
    reason = {200: "OK", 302: "Found"}.get(status, "Generated")
    head = (
        f"HTTP/1.1 {status} {reason}\r\n"
        + "".join(f"{name}: {value}\r\n" for name, value in active)
        + "\r\n"
    ).encode("ascii")
    return head + framed


class _FakeRawSocket:
    def __init__(self, owner: "ScriptedDirectTransport") -> None:
        self.owner = owner
        self.timeout: float | None = None

    def settimeout(self, value: float) -> None:
        self.timeout = value

    def connect(self, address: tuple[str, int]) -> None:
        if address != ("8.8.8.8", 443):
            raise AssertionError("generated peer differs")

    def close(self) -> None:
        return None


class _FakeTLSSocket:
    def __init__(self, owner: "ScriptedDirectTransport") -> None:
        self.owner = owner
        self.sent = False
        self.timeout: float | None = None

    def settimeout(self, value: float) -> None:
        self.timeout = value

    def getpeername(self) -> tuple[str, int]:
        return "8.8.8.8", 443

    def sendall(self, payload: bytes) -> None:
        expected = self.owner.expected_request_bytes
        if expected is None or payload != expected:
            raise AssertionError("exact generated HTTP request bytes differ")
        self.owner.request_serialization_assertions += 1
        self.sent = True

    def makefile(self, _mode: str, buffering: int | None = None) -> io.BytesIO:
        del buffering
        if not self.sent or self.owner.active_response is None:
            raise AssertionError("generated response opened before request send")
        return io.BytesIO(self.owner.active_response)

    def version(self) -> str:
        return "TLSv1.3"

    def close(self) -> None:
        return None


class _FakeSSLContext:
    def __init__(self, owner: "ScriptedDirectTransport") -> None:
        self.owner = owner
        self.minimum_version: object | None = None
        self.check_hostname = False
        self.verify_mode: object | None = None

    def wrap_socket(
        self,
        _raw_socket: _FakeRawSocket,
        *,
        server_hostname: str,
    ) -> _FakeTLSSocket:
        expected = self.owner.active_host
        if server_hostname != expected:
            raise AssertionError("generated SNI differs")
        if (
            self.minimum_version != live.ssl.TLSVersion.TLSv1_2
            or self.check_hostname is not True
            or self.verify_mode != live.ssl.CERT_REQUIRED
        ):
            raise AssertionError("generated TLS context policy differs")
        self.owner.TLS_context_assertions += 1
        return _FakeTLSSocket(self.owner)


class ScriptedDirectTransport:
    """Runs the production direct transport against generated socket/TLS bytes."""

    def __init__(
        self,
        repo_root: Path,
        reservation: live.AttemptReservation,
    ) -> None:
        CI = core.build_generated_CI_fixture(repo_root)
        main_ref = core.strict_json_loads(CI["main_ref"])
        check_runs = core.strict_json_loads(CI["check_runs"])
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
        fixture = core.build_generated_fixture(repo_root)
        exchanges = fixture["exchanges"]
        assert isinstance(exchanges, list)
        self._CI = {
            f"https://{live.CI_HOST}{live.CI_MAIN_PATH}": core.canonical_json_bytes(main_ref),
            (
                f"https://{live.CI_HOST}"
                f"{live.CI_CHECKS_TEMPLATE.format(head=CI['head'].decode('ascii'))}"
            ): core.canonical_json_bytes(check_runs),
            f"https://{live.CI_HOST}{live.CI_WORKFLOW_PATH}": CI["workflow_blob"],
        }
        self._source = {exchange.request_identity_sha256: exchange for exchange in exchanges}
        packet = core.load_packet(repo_root)
        roots = core.build_root_plan(repo_root)
        redirect_root = next(row for row in roots if core._profile_id(row.index_id) == "NEMAR")
        original_identity = core.request_identity(packet, redirect_root)[0]
        original_exchange = self._source[original_identity]
        parsed = urlsplit(redirect_root.url)
        redirect_host = "www.nemar.org" if parsed.hostname == "nemar.org" else "nemar.org"
        self._redirect_url = urlunsplit(("https", redirect_host, parsed.path, parsed.query, ""))
        redirected_identity = core.request_identity(
            packet,
            redirect_root,
            url=self._redirect_url,
            body=redirect_root.body,
        )[0]
        self._source[redirected_identity] = original_exchange
        self._redirect_original_identity = original_identity
        self._redirect_issued = False
        self.head = CI["head"].decode("ascii")
        self.reservation = reservation
        self._production_marker_verifier = live.verify_consumed_marker
        self.calls: list[live.PreparedRequest] = []
        self.input_bytes = 0
        self.marker_guard_observations = 0
        self.request_serialization_assertions = 0
        self.TLS_context_assertions = 0
        self.chunked_responses = 0
        self.redirect_hops = 0
        self.source_responses = 0
        self.active_response: bytes | None = None
        self.active_host: str | None = None
        self.expected_request_bytes: bytes | None = None
        self._monotonic_value = GENERATED_MONOTONIC_START

    def _route(
        self, request: live.PreparedRequest
    ) -> tuple[int, bytes, list[tuple[str, str]], bool]:
        if request.kind == "CI":
            try:
                body = self._CI[request.url]
            except KeyError as exc:
                raise AssertionError("generated CI request differs") from exc
            return 200, body, [("Content-Type", "application/json; charset=utf-8")], False
        if (
            request.request_identity_sha256 == self._redirect_original_identity
            and not self._redirect_issued
        ):
            self._redirect_issued = True
            self.redirect_hops += 1
            return 302, b"", [("Location", self._redirect_url)], False
        try:
            exchange = self._source[request.request_identity_sha256]
        except KeyError as exc:
            raise AssertionError("generated source request differs") from exc
        self.source_responses += 1
        chunked = self.source_responses == 1
        if chunked:
            self.chunked_responses += 1
        return 200, exchange.response_body, list(exchange.response_headers), chunked

    @contextmanager
    def installed(self) -> Iterator[None]:
        with (
            mock.patch.object(live.socket, "getaddrinfo", side_effect=self._getaddrinfo),
            mock.patch.object(live.socket, "socket", side_effect=self._socket),
            mock.patch.object(live.ssl, "create_default_context", side_effect=self._create_context),
            mock.patch.object(live.time, "monotonic", side_effect=self._monotonic),
            mock.patch.object(live.time, "time", return_value=GENERATED_WALL_TIME),
            mock.patch.object(
                live,
                "verify_consumed_marker",
                side_effect=self._observe_production_marker_guard,
            ),
        ):
            yield

    def _monotonic(self) -> float:
        self._monotonic_value += 0.000_001
        return self._monotonic_value

    def _getaddrinfo(self, *_args: object, **_kwargs: object) -> list[tuple[object, ...]]:
        return [
            (
                live.socket.AF_INET,
                live.socket.SOCK_STREAM,
                live.socket.IPPROTO_TCP,
                "",
                ("8.8.8.8", 443),
            )
        ]

    def _socket(self, *_args: object, **_kwargs: object) -> _FakeRawSocket:
        return _FakeRawSocket(self)

    def _create_context(self) -> _FakeSSLContext:
        return _FakeSSLContext(self)

    def _observe_production_marker_guard(self, reservation: live.AttemptReservation) -> None:
        if reservation != self.reservation:
            raise AssertionError("generated marker reservation differs")
        self._production_marker_verifier(reservation)
        self.marker_guard_observations += 1

    def __call__(
        self,
        request: live.PreparedRequest,
        ordinal: int,
        deadline: float,
        started: float,
    ) -> live.ContactResult:
        status, body, headers, chunked = self._route(request)
        host, target = live._request_target(request.url)
        self.active_host = host
        self.expected_request_bytes = (
            f"{request.method} {target} HTTP/1.1\r\n"
            + "".join(f"{name}: {value}\r\n" for name, value in request.headers)
            + "\r\n"
        ).encode("ascii") + request.body
        self.active_response = _HTTP_response(status, headers, body, chunked=chunked)
        try:
            result = live.direct_TLS_contact(request, ordinal, deadline, started)
        finally:
            self.active_response = None
            self.active_host = None
            self.expected_request_bytes = None
        self.calls.append(request)
        self.input_bytes += len(result.body)
        return result


@dataclass(frozen=True, slots=True)
class GeneratedReplay:
    receipt: Mapping[str, object]
    ledger: Mapping[str, object]
    input_bytes: int
    contact_count: int
    marker_bytes: int
    temporary_peak_bytes: int
    marker_refusal_route: str
    marker_guard_observations: int
    request_serialization_assertions: int
    TLS_context_assertions: int
    chunked_responses: int
    redirect_hops: int
    state_transcript: tuple[str, ...]
    audit: live.SemanticAccessAudit


def _run_replay(repo_root: Path) -> GeneratedReplay:
    started = GENERATED_MONOTONIC_START
    authority = _generated_authority("a" * 40)
    with tempfile.TemporaryDirectory(prefix="fmsr1-live-replay-") as directory:
        reservation = live.reserve_consumed_attempt(directory, authority)
        transport = ScriptedDirectTransport(repo_root, reservation)
        if transport.head != authority.local_HEAD:
            raise live.LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "generated HEAD differs")
        states = [
            "CLOSED",
            "LOCAL_PREFLIGHT",
            "RESERVED_PENDING",
            "ARMED_CONSUMED",
        ]
        budget = live.RequestBudget(started=started)
        audit = live.SemanticAccessAudit()
        with transport.installed():
            receipt, ledger = live._run_contact_sequence(
                repo_root,
                authority,
                reservation,
                budget=budget,
                audit=audit,
                states=states,
                contact=transport,
                deadline=started + 10.0,
            )
        states.extend(("FINALIZE", "COMPLETE_OR_PARK"))
        try:
            live.reserve_consumed_attempt(directory, authority)
        except live.LiveWitnessRefusal as exc:
            marker_refusal = exc.code
        else:
            raise live.LiveWitnessRefusal(
                "LIVE_OUTPUT_REFUSE", "generated marker reuse unexpectedly passed"
            )
        temporary_peak = sum(
            path.stat().st_size for path in reservation.attempt_root.iterdir() if path.is_file()
        )
        if (
            budget.CI_requests != 3
            or budget.source_requests != 35
            or budget.total_requests != 38
            or states != list(live.STATE_MACHINE)
            or transport.marker_guard_observations != 38
            or transport.request_serialization_assertions != 38
            or transport.TLS_context_assertions != 38
            or transport.chunked_responses != 1
            or transport.redirect_hops != 1
            or audit.candidate_semantic_accesses != 0
        ):
            raise live.LiveWitnessRefusal(
                "LIVE_RESOURCE_REFUSE", "generated coordinator accounting differs"
            )
        return GeneratedReplay(
            receipt=receipt,
            ledger=ledger,
            input_bytes=transport.input_bytes,
            contact_count=len(transport.calls),
            marker_bytes=len(reservation.marker_payload),
            temporary_peak_bytes=temporary_peak,
            marker_refusal_route=marker_refusal,
            marker_guard_observations=transport.marker_guard_observations,
            request_serialization_assertions=transport.request_serialization_assertions,
            TLS_context_assertions=transport.TLS_context_assertions,
            chunked_responses=transport.chunked_responses,
            redirect_hops=transport.redirect_hops,
            state_transcript=tuple(states),
            audit=audit,
        )


def _raw_HTTP_response(headers: Sequence[tuple[str, str]], body: bytes) -> bytes:
    return (
        b"HTTP/1.1 200 OK\r\n"
        + f"Date: {formatdate(GENERATED_WALL_TIME, usegmt=True)}\r\n".encode("ascii")
        + b"".join(f"{name}: {value}\r\n".encode("ascii") for name, value in headers)
        + b"\r\n"
        + body
    )


def _exercise_raw_direct_response(repo_root: Path, response: bytes) -> live.ContactResult:
    authority = _generated_authority("a" * 40)
    with tempfile.TemporaryDirectory(prefix="fmsr1-live-transport-") as directory:
        reservation = live.reserve_consumed_attempt(directory, authority)
        transport = ScriptedDirectTransport(repo_root, reservation)
        request = replace(
            live._CI_request(live.CI_MAIN_PATH),
            maximum_response_bytes=64,
            maximum_wire_response_bytes=64,
        )
        host, target = live._request_target(request.url)
        transport.active_host = host
        transport.expected_request_bytes = (
            f"{request.method} {target} HTTP/1.1\r\n"
            + "".join(f"{name}: {value}\r\n" for name, value in request.headers)
            + "\r\n"
        ).encode("ascii")
        transport.active_response = response
        try:
            with transport.installed():
                return live.direct_TLS_contact(
                    request,
                    0,
                    GENERATED_MONOTONIC_START + 10.0,
                    GENERATED_MONOTONIC_START,
                )
        finally:
            transport.active_response = None
            transport.active_host = None
            transport.expected_request_bytes = None


def _run_direct_transport_matrix(repo_root: Path) -> tuple[list[str], int]:
    responses = (
        (b"HTTP/1.1 100 Continue\r\n\r\n" + _raw_HTTP_response((("Content-Length", "0"),), b"")),
        _raw_HTTP_response(
            (("Content-Length", "0"), ("Transfer-Encoding", "chunked")),
            b"0\r\n\r\n",
        ),
        _raw_HTTP_response((("Transfer-Encoding", "chunked"),), b"Z\r\n"),
        _raw_HTTP_response((("Content-Length", "2"),), b"x"),
        _raw_HTTP_response((("Content-Length", "65"),), b""),
        _raw_HTTP_response(
            (("Transfer-Encoding", "chunked"),),
            b"3C\r\n" + (b"x" * 60) + b"\r\n0\r\n\r\n",
        ),
    )
    observations: list[str] = []
    for response in responses:
        try:
            _exercise_raw_direct_response(repo_root, response)
        except live.LiveWitnessPark as exc:
            observations.append(f"{exc.route}:{exc.reason_class}")
        else:
            raise live.LiveWitnessRefusal(
                "LIVE_OUTPUT_REFUSE", "generated transport refusal unexpectedly passed"
            )
    connection_close = _exercise_raw_direct_response(
        repo_root,
        _raw_HTTP_response((), b"{}"),
    )
    if (
        connection_close.transfer_framing != "connection_close"
        or connection_close.body != b"{}"
        or len(observations) != len(responses)
    ):
        raise live.LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "generated transport matrix differs")
    return observations, 1


def _observe(
    routes: list[str],
    operation: Callable[[], object],
) -> None:
    try:
        operation()
    except live.LiveWitnessRefusal as exc:
        routes.append(exc.code)
    except live.LiveWitnessPark as exc:
        routes.append(exc.route)
    except core.WitnessRefusal as exc:
        routes.append(exc.route)
    else:
        raise live.LiveWitnessRefusal(
            "LIVE_OUTPUT_REFUSE", "generated refusal case unexpectedly passed"
        )


def _claim_many(kind: str, count: int) -> None:
    budget = live.RequestBudget(started=time.monotonic())
    for _index in range(count):
        budget.claim(kind)
    budget.claim(kind)


def _mixed_overclaim() -> None:
    budget = live.RequestBudget(started=time.monotonic())
    for _index in range(live.MAX_CI_REQUESTS):
        budget.claim("CI")
    for _index in range(live.MAX_SOURCE_REQUESTS):
        budget.claim("SOURCE")
    budget.claim("SOURCE")


def _byte_overclaim(kind: str, maximum: int) -> None:
    budget = live.RequestBudget(started=time.monotonic())
    budget.add_body(kind, maximum, maximum)
    budget.add_body(kind, 1, 1)


def _result_fixture(authority: live.ExecutionAuthority) -> dict[str, object]:
    result = live._base_result(
        authority,
        live.RequestBudget(started=time.monotonic()),
        route="WITNESS_CAP_PARK",
        started=time.monotonic(),
        state_transcript=(
            "CLOSED",
            "LOCAL_PREFLIGHT",
            "FINALIZE",
            "COMPLETE_OR_PARK",
        ),
    )
    result["park_reason_class"] = "GENERATED"
    result["consumed_marker_bytes"] = 1
    result["CI_W0_receipt"] = None
    return result


def _generated_contact_result(body: bytes, *, status: int) -> live.ContactResult:
    headers = (
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Encoding", "identity"),
        ("Content-Length", str(len(body))),
    )
    peer = _sha256(b"8.8.8.8")
    return live.ContactResult(
        status=status,
        headers=headers,
        body=body,
        DNS_answer_set_sha256=peer,
        selected_peer_sha256=peer,
        post_connect_peer_sha256=peer,
        selected_and_post_connect_peer_equal_and_global=True,
        TLS_version="TLSv1.3",
        response_headers_sha256=_sha256(core.canonical_json_bytes([list(row) for row in headers])),
        content_encoding="identity",
        transfer_framing="content_length",
        wire_body_bytes=len(body),
        request_elapsed_nanoseconds=1,
        whole_invocation_elapsed_nanoseconds=2,
    )


def _run_refusal_matrix(repo_root: Path, marker_refusal: str) -> list[str]:
    routes: list[str] = [marker_refusal]
    baseline = build_generated_execution_decision()
    for key, value in (
        ("packet_id", "OTHER"),
        ("maintainer_words_sha256", "0" * 64),
        ("packet_artifacts", []),
    ):
        mutated = copy.deepcopy(baseline)
        mutated[key] = value
        _observe(routes, lambda mutated=mutated: live.validate_execution_decision(mutated))

    missing_record = copy.deepcopy(baseline)
    implementation = missing_record["green_live_implementation"]
    assert isinstance(implementation, dict)
    implementation.pop("implementation_record")
    _observe(routes, lambda: live.validate_execution_decision(missing_record))

    _observe(routes, lambda: _claim_many("CI", live.MAX_CI_REQUESTS))
    _observe(routes, lambda: _claim_many("SOURCE", live.MAX_SOURCE_REQUESTS))
    _observe(routes, _mixed_overclaim)
    _observe(routes, lambda: _byte_overclaim("CI", live.MAX_CI_BYTES))
    _observe(
        routes,
        lambda: _byte_overclaim("SOURCE", live.MAX_SOURCE_WIRE_BYTES),
    )
    _observe(
        routes,
        lambda: live._validate_environment(
            {**{key: "1" for key in live.THREAD_ENV_KEYS}, "HTTP_PROXY": "set"}
        ),
    )
    _observe(routes, lambda: live._validate_environment({}))

    packet = core.load_packet(repo_root)
    root = next(row for row in core.build_root_plan(repo_root) if "?" in row.url)
    _observe(
        routes,
        lambda: live._canonical_redirect_url(packet, root, root.url, f"{root.url}&page=999"),
    )
    _observe(
        routes,
        lambda: live._strict_CI_JSON(_generated_contact_result(b"{}", status=500)),
    )

    authority = _generated_authority("a" * 40)
    leaked = _result_fixture(authority)
    leaked["target"] = "REFERENCE_TARGET_DO_NOT_RETAIN_0"
    _observe(routes, lambda: live._validate_result(leaked, allow_complete=False))
    oversized = _result_fixture(authority)
    oversized["padding"] = "x" * live.MAX_RETAINED_BYTES
    _observe(routes, lambda: live._render_result_artifacts(oversized, None))
    return routes


def _render_report(report: Mapping[str, object]) -> tuple[dict[str, object], bytes]:
    rendered = dict(report)
    rendered["report_bytes"] = 0
    for _iteration in range(8):
        payload = core.canonical_json_bytes(rendered, newline=True)
        if rendered["report_bytes"] == len(payload):
            if len(payload) > MAX_QUALIFICATION_REPORT_BYTES:
                raise live.LiveWitnessRefusal(
                    "LIVE_OUTPUT_REFUSE", "qualification report cap exceeded"
                )
            return rendered, payload
        rendered["report_bytes"] = len(payload)
    raise live.LiveWitnessRefusal(
        "LIVE_OUTPUT_REFUSE", "qualification byte accounting did not converge"
    )


def run_generated_live_qualification(
    repo_root: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> dict[str, object]:
    if QUALIFICATION_CONSUMED:
        raise live.LiveWitnessRefusal(
            "LIVE_AUTHORITY_REFUSE", "generated live-adapter qualification is consumed"
        )
    root = (
        Path(repo_root).resolve() if repo_root is not None else Path(__file__).resolve().parents[3]
    )
    started = time.monotonic()
    live._validate_environment(os.environ if environ is None else environ)
    load_green_live_implementation_decision(root)
    first = _run_replay(root)
    second = _run_replay(root)
    if first.receipt != second.receipt or first.ledger != second.ledger:
        raise live.LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "generated replay differs")
    public_ledger = core.canonical_json_bytes(first.ledger, newline=True)
    if POISON_PREFIX in public_ledger:
        raise live.LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "generated target poison escaped")
    if (
        first.state_transcript != live.STATE_MACHINE
        or second.state_transcript != live.STATE_MACHINE
        or first.marker_refusal_route != second.marker_refusal_route
        or first.audit.candidate_semantic_accesses != 0
        or second.audit.candidate_semantic_accesses != 0
        or first.audit.control_fields_accessed <= 0
        or second.audit.control_fields_accessed <= 0
        or first.audit.opaque_members_skipped <= 0
        or second.audit.opaque_members_skipped <= 0
    ):
        raise live.LiveWitnessRefusal(
            "LIVE_OUTPUT_REFUSE", "generated access or state accounting differs"
        )
    generated_temporary_peak_bytes = max(first.temporary_peak_bytes, second.temporary_peak_bytes)
    if generated_temporary_peak_bytes > live.MAX_TEMPORARY_BYTES:
        raise live.LiveWitnessRefusal("LIVE_RESOURCE_REFUSE", "generated temporary cap exceeded")

    refusal_routes = _run_refusal_matrix(root, first.marker_refusal_route)
    direct_transport_observations, connection_close_assertions = _run_direct_transport_matrix(root)
    runtime = time.monotonic() - started
    peak_RSS = live._peak_rss_bytes()
    generated_input_bytes = first.input_bytes + second.input_bytes
    if (
        runtime > MAX_QUALIFICATION_SECONDS
        or peak_RSS > live.MAX_PEAK_RSS_BYTES
        or generated_input_bytes > MAX_GENERATED_INPUT_BYTES
    ):
        raise live.LiveWitnessRefusal(
            "LIVE_RESOURCE_REFUSE", "generated qualification cap exceeded"
        )
    report = {
        "schema_name": ("neurodecodekit.fresh_motor_source_identity_witness_live_qualification"),
        "schema_version": live.SCHEMA_VERSION,
        "packet_id": live.PACKET_ID,
        "implementation_id": live.LIVE_IMPLEMENTATION_ID,
        "qualification_id": QUALIFICATION_ID,
        "route": "GENERATED_LIVE_ADAPTER_QUALIFIED",
        "deterministic_replays": 2,
        "CI_W0_validations": 2,
        "profile_count": len(first.ledger["profiles"]),
        "root_count": first.ledger["total_root_count"],
        "page_count": first.ledger["total_page_count"],
        "generated_transport_calls": first.contact_count + second.contact_count,
        "marker_before_contact_assertions": (
            first.marker_guard_observations + second.marker_guard_observations
        ),
        "exact_request_serialization_assertions": (
            first.request_serialization_assertions + second.request_serialization_assertions
        ),
        "TLS_context_policy_assertions": (
            first.TLS_context_assertions + second.TLS_context_assertions
        ),
        "chunked_response_assertions": (first.chunked_responses + second.chunked_responses),
        "redirect_hop_assertions": first.redirect_hops + second.redirect_hops,
        "candidate_semantic_accesses": (
            first.audit.candidate_semantic_accesses + second.audit.candidate_semantic_accesses
        ),
        "pagination_control_fields_accessed": (
            first.audit.control_fields_accessed + second.audit.control_fields_accessed
        ),
        "opaque_members_skipped": (
            first.audit.opaque_members_skipped + second.audit.opaque_members_skipped
        ),
        "generated_input_bytes": generated_input_bytes,
        "generated_temporary_peak_bytes": generated_temporary_peak_bytes,
        "generated_marker_bytes": first.marker_bytes,
        "generated_retained_bytes": 0,
        "refusal_observations": len(refusal_routes),
        "refusal_routes": sorted(set(refusal_routes)),
        "direct_transport_refusal_observations": len(direct_transport_observations),
        "direct_transport_refusal_reasons": direct_transport_observations,
        "connection_close_assertions": connection_close_assertions,
        "global_ledger_sha256": first.ledger["canonical_global_ledger_sha256"],
        "CI_W0_receipt_sha256": _sha256(core.canonical_json_bytes(first.receipt, newline=True)),
        "runtime_seconds": runtime,
        "peak_RSS_bytes": peak_RSS,
        "CPU_threads": 1,
        "workers": 1,
        "numerical_jobs": 1,
        "producer_is_causal": "not_applicable_source_identity_only",
        "end_to_end_latency_measured": False,
        "warnings": [
            "Generated fixtures only; DNS, sockets, GitHub, and official indexes were not contacted.",
            "Candidate fixture bodies were retained only in memory and public outputs contain hashes and counts only.",
            "This qualification establishes adapter behavior, not source identity or neural evidence.",
        ],
        "unavailable_fields": list(live.LIVE_UNAVAILABLE_FIELDS),
        "operation_counters": {
            "network_requests": 0,
            "network_bytes": 0,
            "official_index_requests": 0,
            "candidate_semantic_operations": 0,
            "source_selections": 0,
            "payload_or_neural_reads": 0,
            "target_or_label_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "scoring_events": 0,
            "scientific_claim_upgrades": 0,
        },
        "claim_boundary": dict(core.CLAIM_BOUNDARY),
    }
    core._walk_public(report)
    rendered, payload = _render_report(report)
    if POISON_PREFIX in payload:
        raise live.LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "qualification target poison escaped")
    return rendered
