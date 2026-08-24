import copy
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import (
    marc2_selection_sufficiency_private_cohort_freeze as vr39p,
)


class SelectionSufficiencyPrivateCohortFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environment = dict(vr39p.THREAD_ENVIRONMENT)

    def test_registered_authority_and_green_decision_are_exact(self):
        request = vr39p.load_registered_request()
        decision = vr39p.load_registered_decision()
        vr39p._verify_authority_mapping(request, decision)
        vr39p._verify_decision_proof()
        self.assertEqual(request["lane_id"], "MARC2-VR39P")
        self.assertEqual(decision["user_authorization"]["actual_message_verbatim"], "continue")
        self.assertEqual(vr39p._verify_fixed_inputs(request, decision), 374_043)

    def test_plan_is_generated_open_and_private_proof_gated(self):
        plan = vr39p.build_plan()
        self.assertEqual(plan["generated_paths"], 168)
        self.assertEqual(plan["VR33A_calls"], 168)
        self.assertEqual(plan["readiness_provider_calls"], 504)
        self.assertEqual(plan["readiness_sleeper_calls"], 336)
        self.assertEqual(plan["VR38A_calls"], 84)
        self.assertEqual(plan["generated_cohort_writes"], 64)
        self.assertEqual(
            plan["route_counts"],
            {"MARC2VR39P-R1": 64, "MARC2VR39P-R2": 104},
        )
        self.assertEqual(plan["private_invocation_limit_after_proof"], 1)
        self.assertEqual(plan["neural_payload_bytes"], 0)
        self.assertEqual(plan["target_bytes"], 0)
        self.assertEqual(plan["scientific_ceiling"], "none")

    def test_cli_has_only_fixed_commands_and_no_overrides(self):
        parser = vr39p._parser()
        for command in ("plan", "qualify", "inspect", "execute"):
            self.assertEqual(parser.parse_args([command]).command, command)
        with self.assertRaises(SystemExit):
            parser.parse_args(["execute", "--source", "/tmp/other"])
        with self.assertRaises(SystemExit):
            parser.parse_args(["qualify", "--output", "/tmp/other"])

    def test_generated_readiness_calls_are_exact(self):
        ready, providers, sleepers, input_bytes = vr39p._collect_generated_readiness("PPP")
        self.assertTrue(ready.ready)
        self.assertEqual((providers, sleepers), (3, 2))
        self.assertGreater(input_bytes, 0)
        not_ready, providers, sleepers, _ = vr39p._collect_generated_readiness("FFF")
        self.assertFalse(not_ready.ready)
        self.assertEqual((providers, sleepers), (3, 2))
        for pattern in vr39p.DIRECT_NONPASSING_PATTERNS:
            with self.subTest(pattern=pattern):
                not_ready, providers, sleepers, _ = vr39p._collect_generated_readiness(pattern)
                self.assertFalse(not_ready.ready)
                self.assertEqual((providers, sleepers), (3, 2))

    def test_ready_case_matrix_collapses_to_two_public_routes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for index, case in enumerate(vr39p.CASES):
                case_root = root / str(index)
                case_root.mkdir()
                result = vr39p._run_generated_case(
                    pattern="PPP",
                    case=case,
                    order="canonical",
                    root=case_root,
                )
                success = index < 16
                self.assertEqual(
                    result["route"],
                    vr39p.PRIVATE_ROUTES[0 if success else 1],
                )
                self.assertEqual(result["cohort_file_writes"], int(success))
                self.assertEqual(
                    result["nonce_provider_calls"],
                    int(success or case == "uncompressed_payload_ceiling_exceeded"),
                )
                self.assertEqual(result["VR38A_calls"], 1)
                self.assertTrue(result["source_unchanged"])
                if success:
                    expected_upstream = "MARC2VR38A-G1" if index % 2 == 0 else "MARC2VR38A-G2"
                    self.assertEqual(result["VR38A_route"], expected_upstream)

    def test_not_ready_constructs_no_source_and_calls_no_vr38a(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with mock.patch.object(
                vr39p.vr38a,
                "build_generated_case",
                side_effect=AssertionError("source factory must not run"),
            ):
                result = vr39p._run_generated_case(
                    pattern="FFF",
                    case=vr39p.CASES[0],
                    order="canonical",
                    root=root,
                )
                self.assertEqual(stat.S_IMODE((root / "output").stat().st_mode), 0o700)
        self.assertEqual(result["route"], vr39p.PRIVATE_ROUTES[1])
        self.assertEqual(result["source_constructions"], 0)
        self.assertEqual(result["source_content_opens"], 0)
        self.assertEqual(result["VR38A_calls"], 0)
        self.assertEqual(result["cohort_file_writes"], 0)
        self.assertEqual(result["nonce_provider_calls"], 0)

    def test_canonical_and_reversed_sources_preserve_semantic_selection(self):
        for case in ("selected_12_public_map_exact", "selected_19_optional_run_drift"):
            canonical = vr39p.vr38a.select_generated_source(
                vr39p._build_generated_source(case, "canonical")
            )
            reversed_outcome = vr39p.vr38a.select_generated_source(
                vr39p._build_generated_source(case, "reversed")
            )
            with self.subTest(case=case):
                self.assertEqual(canonical.semantic_sha256, reversed_outcome.semantic_sha256)
                self.assertEqual(
                    canonical.selection.selection_hashes["selection_identity_sha256"],
                    reversed_outcome.selection.selection_hashes["selection_identity_sha256"],
                )

    def test_private_manifest_supports_12_through_19_and_hmac(self):
        for count in range(12, 20):
            with self.subTest(count=count):
                source = vr39p._build_generated_source(
                    f"selected_{count}_public_map_exact", "canonical"
                )
                outcome = vr39p.vr38a.select_generated_source(source)
                nonce = bytes([count]) * vr39p.PRIVATE_NONCE_BYTES
                manifest, commitment = vr39p._build_private_manifest(
                    outcome,
                    raw_source_sha256=vr39p._sha256_bytes(vr39p.vr38a._source_bytes(source)),
                    nonce=nonce,
                )
                self.assertEqual(manifest["schema_name"], vr39p.PRIVATE_MANIFEST_SCHEMA_NAME)
                self.assertEqual(
                    manifest["proof_posture"],
                    "target_free_private_structural_selection_no_neural_payload",
                )
                self.assertEqual(len(manifest["rows"]), count * 24)
                self.assertEqual(manifest["cohort_summary"]["selected_subjects"], count)
                self.assertEqual(manifest["split_summary"]["selected_run_bundles"], count * 6)
                self.assertTrue(vr39p._verify_private_commitment(manifest, commitment))
                self.assertEqual(
                    manifest["hash_bindings"]["selection_identity_sha256"],
                    outcome.selection.selection_hashes["selection_identity_sha256"],
                )
                for row in manifest["rows"]:
                    self.assertEqual(
                        set(row["source_hashes"]),
                        {
                            "contract_sha256",
                            "raw_source_file_sha256",
                            "canonical_private_inventory_sha256",
                        },
                    )
                tampered = dict(manifest)
                tampered["task"] = "wrong"
                self.assertFalse(vr39p._verify_private_commitment(tampered, commitment))
                bad_commitment = dict(manifest)
                bad_commitment["commitment"] = dict(manifest["commitment"])
                bad_commitment["commitment"]["private_nonce_hex"] = "00"
                self.assertFalse(vr39p._verify_private_commitment(bad_commitment, commitment))
                for key, value in (
                    ("scheme", "wrong"),
                    ("domain_separator_utf8", "wrong"),
                    ("cohort_commitment_sha256", "0" * 64),
                ):
                    malformed = dict(manifest)
                    malformed["commitment"] = dict(manifest["commitment"])
                    malformed["commitment"][key] = value
                    self.assertFalse(vr39p._verify_private_commitment(malformed, commitment))
                self.assertNotIn(
                    "generated_inventory_sha256",
                    vr39p._canonical_json_bytes(manifest).decode("ascii"),
                )

    def test_private_manifest_is_mode_0600(self):
        source = vr39p._build_generated_source("selected_12_public_map_exact", "canonical")
        outcome = vr39p.vr38a.select_generated_source(source)
        manifest, _ = vr39p._build_private_manifest(
            outcome,
            raw_source_sha256=vr39p._sha256_bytes(vr39p.vr38a._source_bytes(source)),
            nonce=b"x" * vr39p.PRIVATE_NONCE_BYTES,
        )
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp).resolve() / "cohort.private.json"
            payload = vr39p._canonical_json_bytes(manifest)
            self.assertEqual(vr39p._write_exclusive(path, payload), len(payload))
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_private_manifest_revalidates_frozen_cohort_semantics(self):
        source = vr39p._build_generated_source("selected_12_public_map_exact", "canonical")
        outcome = vr39p.vr38a.select_generated_source(source)
        raw_sha256 = vr39p._sha256_bytes(vr39p.vr38a._source_bytes(source))
        mutations = {
            "split_session": lambda item: item.selection.split_summary.__setitem__(
                "fit_session", "ses-02"
            ),
            "maximal_prefix": lambda item: item.selection.cohort_summary.__setitem__(
                "selection_is_maximal_contiguous_rank_prefix", False
            ),
            "row_session": lambda item: item.selection.private_manifest["rows"][0].__setitem__(
                "session_id", "ses-03"
            ),
            "row_provenance": lambda item: item.selection.private_manifest["rows"][0][
                "source_hashes"
            ].__setitem__("contract_sha256", "wrong"),
        }
        for name, mutate in mutations.items():
            candidate = copy.deepcopy(outcome)
            mutate(candidate)
            with (
                self.subTest(name=name),
                self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal),
            ):
                vr39p._build_private_manifest(
                    candidate,
                    raw_source_sha256=raw_sha256,
                    nonce=b"x" * vr39p.PRIVATE_NONCE_BYTES,
                )

    def test_strict_json_rejects_duplicate_nonfinite_bom_and_noncanonical(self):
        invalid = [
            b'{"a":1,"a":2}\n',
            b'{"a":NaN}\n',
            b"\xef\xbb\xbf{}\n",
            b'{"a":"\x00"}\n',
            b"[]\n",
        ]
        for payload in invalid:
            with (
                self.subTest(payload=payload),
                self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal),
            ):
                vr39p._strict_json(payload)
        with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
            vr39p._strict_json(b'{ "a": 1 }\n', canonical=True)

    def test_bound_source_rejects_symlink_wrong_mode_size_and_hash(self):
        payload = vr39p._canonical_json_bytes({"schema_name": "fixture", "entries": [{"x": 1}]})
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            source = root / "source.json"
            source.write_bytes(payload)
            os.chmod(source, 0o600)
            binding = vr39p.SourceBinding(
                bytes=len(payload),
                sha256=vr39p._sha256_bytes(payload),
                schema_name="fixture",
                rows=1,
                mode=0o600,
            )
            self.assertEqual(vr39p._read_bound_source_once(source, binding)["entries"], [{"x": 1}])
            link = root / "link.json"
            link.symlink_to(source)
            with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
                vr39p._read_bound_source_once(link, binding)
            os.chmod(source, 0o644)
            with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
                vr39p._read_bound_source_once(source, binding)
            os.chmod(source, 0o600)
            bad = vr39p.SourceBinding(
                bytes=len(payload),
                sha256="0" * 64,
                schema_name="fixture",
                rows=1,
                mode=0o600,
            )
            with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
                vr39p._read_bound_source_once(source, bad)

            real_parent = root / "real-parent"
            real_parent.mkdir()
            nested = real_parent / "source.json"
            nested.write_bytes(payload)
            os.chmod(nested, 0o600)
            linked_parent = root / "linked-parent"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
                vr39p._read_bound_source_once(linked_parent / "source.json", binding)

    def test_exclusive_writer_refuses_overwrite_and_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            path = root / "out.json"
            vr39p._write_exclusive(path, b"{}\n")
            with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
                vr39p._write_exclusive(path, b"{}\n")
            target = root / "target.json"
            target.write_bytes(b"{}\n")
            link = root / "link.json"
            link.symlink_to(target)
            with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
                vr39p._write_exclusive(link, b"{}\n")
            parent_target = root / "parent-target"
            parent_target.mkdir()
            parent_link = root / "parent-link"
            parent_link.symlink_to(parent_target, target_is_directory=True)
            with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
                vr39p._write_exclusive(parent_link / "refused.json", b"{}\n")
            self.assertFalse((parent_target / "refused.json").exists())

    def test_short_write_and_prewrite_crash_never_create_valid_completion(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            short = root / "short.json"
            with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
                vr39p._write_exclusive(short, b"{}\n", writer=lambda _fd, _view: 0)
            self.assertTrue(short.exists())
            self.assertFalse(vr39p._completion_is_valid(short))
            for name in (
                "source.json",
                vr39p.MARKER_NAME,
                "readiness.v0.json",
                vr39p.PRIVATE_MANIFEST_NAME,
                vr39p.REPORT_NAME,
                vr39p.COMPLETION_NAME,
            ):
                target = root / name
                with (
                    self.subTest(name=name),
                    self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal),
                ):
                    vr39p._write_exclusive(
                        target,
                        b"{}\n",
                        before_write=vr39p._raise_injected_crash,
                    )
                self.assertFalse(target.exists())

    def test_public_firewall_rejects_every_forbidden_key(self):
        for key in vr39p.FORBIDDEN_PUBLIC_KEYS:
            with (
                self.subTest(key=key),
                self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal),
            ):
                vr39p._assert_aggregate_safe({"nested": [{key: "x"}]})
        report = vr39p._case_report(
            route=vr39p.PRIVATE_ROUTES[1],
            commitment=None,
            generated=True,
        )
        self.assertEqual(set(report), vr39p.PUBLIC_FIELDS)
        self.assertEqual(report["commitment_scheme"], "HMAC-SHA256-v0")

    def test_inspection_requires_exact_public_allowlist(self):
        report = vr39p._case_report(
            route=vr39p.PRIVATE_ROUTES[1],
            commitment=None,
            generated=True,
        )
        report["secret"] = "not-allowlisted"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp).resolve() / "report.json"
            vr39p._write_exclusive(
                path,
                vr39p._canonical_json_bytes(report),
                mode=0o644,
            )
            with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
                vr39p._inspect_report_file(path, allow_generated=True)

    def test_public_r2_is_byte_identical_and_r1_only_changes_commitment(self):
        r2_a = vr39p._case_report(route=vr39p.PRIVATE_ROUTES[1], commitment=None, generated=True)
        r2_b = vr39p._case_report(route=vr39p.PRIVATE_ROUTES[1], commitment=None, generated=True)
        self.assertEqual(vr39p._canonical_json_bytes(r2_a), vr39p._canonical_json_bytes(r2_b))
        self.assertEqual(r2_a["commitment_scheme"], "HMAC-SHA256-v0")
        r1_a = vr39p._case_report(
            route=vr39p.PRIVATE_ROUTES[0], commitment="a" * 64, generated=True
        )
        r1_b = vr39p._case_report(
            route=vr39p.PRIVATE_ROUTES[0], commitment="b" * 64, generated=True
        )
        self.assertNotEqual(vr39p._canonical_json_bytes(r1_a), vr39p._canonical_json_bytes(r1_b))
        r1_a["cohort_commitment_sha256"] = None
        r1_b["cohort_commitment_sha256"] = None
        self.assertEqual(r1_a, r1_b)

    def test_missing_completion_is_invalid(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            output_root = root / "output"
            completion = output_root / vr39p.COMPLETION_NAME
            self.assertFalse(vr39p._completion_is_valid(completion))
            vr39p._run_generated_case(
                pattern="FFF",
                case=vr39p.CASES[0],
                order="canonical",
                root=root,
            )
            self.assertTrue(vr39p._completion_is_valid(completion))
            target = root / "target.json"
            vr39p._write_exclusive(target, completion.read_bytes())
            symlink = output_root / "completion-link.json"
            symlink.symlink_to(target)
            self.assertFalse(vr39p._completion_is_valid(symlink))
            report = output_root / vr39p.REPORT_NAME
            report.write_bytes(b"{}\n")
            os.chmod(report, 0o644)
            self.assertFalse(vr39p._completion_is_valid(completion))

    def test_bad_generated_nonce_collapses_to_r2_without_cohort(self):
        with tempfile.TemporaryDirectory() as temp:
            result = vr39p._run_generated_case(
                pattern="PPP",
                case="selected_12_public_map_exact",
                order="canonical",
                root=Path(temp),
                nonce_provider=lambda _case, _order: b"short",
            )
        self.assertEqual(result["route"], vr39p.PRIVATE_ROUTES[1])
        self.assertEqual(result["nonce_provider_calls"], 1)
        self.assertEqual(result["cohort_file_writes"], 0)

    def test_source_mutation_collapses_to_r2_without_cohort(self):
        def mutating_selector(source):
            result = vr39p._apply_vr38a(source)
            source["entries"].append(dict(source["entries"][0]))
            return result

        with tempfile.TemporaryDirectory() as temp:
            result = vr39p._run_generated_case(
                pattern="PPP",
                case="selected_12_public_map_exact",
                order="canonical",
                root=Path(temp),
                selector=mutating_selector,
            )
        self.assertEqual(result["route"], vr39p.PRIVATE_ROUTES[1])
        self.assertFalse(result["source_unchanged"])
        self.assertEqual(result["cohort_file_writes"], 0)

    def test_output_root_replacement_is_refused_after_marker(self):
        def replace_output_root(paths):
            moved = paths.output_root.with_name("moved-output")
            paths.output_root.rename(moved)
            paths.output_root.mkdir(mode=0o700)

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
                vr39p._run_generated_case(
                    pattern="PPP",
                    case="selected_12_public_map_exact",
                    order="canonical",
                    root=root,
                    after_marker=replace_output_root,
                )
            self.assertFalse((root / "output" / vr39p.COMPLETION_NAME).exists())

    def test_storage_boundaries_fail_closed(self):
        self.assertEqual(
            vr39p._storage_totals(
                [
                    {
                        "compressed_size": vr39p.MAX_COMPRESSED_BYTES,
                        "uncompressed_size": (
                            vr39p.MAX_PEAK_INCREMENTAL_DISK_BYTES
                            - vr39p.DERIVATIVE_RESERVE_BYTES
                            - vr39p.TEMPORARY_RESERVE_BYTES
                        ),
                    }
                ]
            )["selected_compressed_bytes"],
            vr39p.MAX_COMPRESSED_BYTES,
        )
        with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
            vr39p._storage_totals(
                [
                    {
                        "compressed_size": vr39p.MAX_COMPRESSED_BYTES + 1,
                        "uncompressed_size": 1,
                    }
                ]
            )

    def test_direct_refusal_matrix_exceeds_registered_minimum(self):
        counts = vr39p._run_direct_refusals(
            vr39p.load_registered_request(), vr39p.load_registered_decision()
        )
        self.assertGreaterEqual(sum(counts.values()), 200)
        self.assertTrue(set(counts).issubset(vr39p.REFUSAL_ROUTES))
        critical_routes, critical_classes = vr39p._run_critical_refusal_witnesses(
            vr39p.load_registered_request(), vr39p.load_registered_decision()
        )
        self.assertEqual(len(critical_classes), 12)
        self.assertEqual(set(critical_classes.values()), {1})
        self.assertTrue(set(critical_routes).issubset(vr39p.REFUSAL_ROUTES))

    def test_execute_and_inspect_refuse_before_green_implementation_proof(self):
        refusal = vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal(
            vr39p.REFUSAL_ROUTES[1], "proof blocked"
        )
        with (
            mock.patch.object(vr39p, "_require_green_implementation", side_effect=refusal),
            mock.patch.object(vr39p, "load_registered_request") as load_request,
            mock.patch.object(vr39p, "_repo_root") as repo_root,
        ):
            with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal) as ctx:
                vr39p.execute_fixed()
            self.assertEqual(ctx.exception.route, vr39p.REFUSAL_ROUTES[1])
            load_request.assert_not_called()
            repo_root.assert_not_called()
        with (
            tempfile.TemporaryDirectory() as temp,
            self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal),
        ):
            vr39p._require_green_implementation(Path(temp))

    def test_resource_checks_fail_closed_without_running_matrix(self):
        with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal) as ctx:
            vr39p._assert_generated_resources(121.0, 1, 1)
        self.assertEqual(ctx.exception.route, vr39p.REFUSAL_ROUTES[9])
        with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
            vr39p._assert_generated_resources(1.0, vr39p.MAX_RSS_BYTES, 1)
        with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
            vr39p._assert_generated_resources(1.0, 1, vr39p.MAX_OUTPUT_BYTES + 1)
        with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
            vr39p._assert_generated_resources(
                1.0,
                1,
                1,
                vr39p.MAX_MATERIALIZED_GENERATED_INPUT_BYTES + 1,
                1,
            )
        with self.assertRaises(vr39p.SelectionSufficiencyPrivateCohortFreezeRefusal):
            vr39p._assert_generated_resources(
                1.0,
                1,
                1,
                1,
                vr39p.MAX_MATERIALIZED_GENERATED_INPUT_BYTES + vr39p.MAX_OUTPUT_BYTES + 1,
            )


if __name__ == "__main__":
    unittest.main()
