from __future__ import annotations

import os
import tempfile
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import fresh_motor_source_admission as admission

THREAD_ENVIRONMENT = {key: "1" for key in admission.THREAD_ENV_KEYS}


class InjectedPostArmFailure(RuntimeError):
    """A generated unit-test fault after the one-shot root is armed."""


class FreshMotorSourceAdmissionDurabilityTests(unittest.TestCase):
    @contextmanager
    def assert_refusal(self, route: str) -> Iterator[None]:
        with self.assertRaises(admission.FMSR1AdmissionRefusal) as caught:
            yield
        self.assertEqual(caught.exception.route, route)

    @staticmethod
    def marker_bytes() -> bytes:
        return admission.canonical_json_bytes(
            {
                "execution_ordinal": 1,
                "generated": True,
                "protocol_id": admission.PROTOCOL_ID,
                "stage": "OFFICIAL_GENERATED_QUALIFICATION",
            }
        )

    def test_official_creation_fsyncs_each_directory_once_in_order(self) -> None:
        with tempfile.TemporaryDirectory(prefix="fmsr1-durability-") as directory:
            repo_root = Path(directory) / "repo"
            repo_root.mkdir()
            work_root = repo_root / admission.OFFICIAL_QUALIFICATION_ROOT.parent
            attempt_root = repo_root / admission.OFFICIAL_QUALIFICATION_ROOT
            observed: list[str] = []

            def record_directory_fsync(file_descriptor: int) -> None:
                opened = os.fstat(file_descriptor)
                for name, path in (
                    ("repository_root", repo_root),
                    ("work_root", work_root),
                    ("attempt_root", attempt_root),
                ):
                    try:
                        candidate = os.lstat(path)
                    except FileNotFoundError:
                        continue
                    if (opened.st_dev, opened.st_ino) == (
                        candidate.st_dev,
                        candidate.st_ino,
                    ):
                        observed.append(name)
                        return
                self.fail("directory fsync used an unexpected file descriptor")

            with admission._official_qualification_root(
                repo_root,
                directory_fsync=record_directory_fsync,
            ) as (created_root, marker):
                self.assertEqual(created_root, attempt_root.resolve(strict=True))
                self.assertEqual(marker["directory_fsyncs"], 3)

            self.assertEqual(
                observed,
                ["repository_root", "work_root", "attempt_root"],
            )

    def test_repository_root_symlink_or_non_directory_refuses_pre_arm(self) -> None:
        with tempfile.TemporaryDirectory(prefix="fmsr1-root-types-") as directory:
            parent = Path(directory)
            real_repo = parent / "real-repo"
            real_repo.mkdir()
            linked_repo = parent / "linked-repo"
            linked_repo.symlink_to(real_repo, target_is_directory=True)

            with (
                self.assert_refusal("ORDER_REFUSE"),
                admission._official_qualification_root(linked_repo),
            ):
                pass
            self.assertFalse(
                (real_repo / admission.OFFICIAL_QUALIFICATION_ROOT.parent).exists()
            )

            file_root = parent / "not-a-directory"
            file_root.write_bytes(b"generated")
            with (
                self.assert_refusal("ORDER_REFUSE"),
                admission._official_qualification_root(file_root),
            ):
                pass

    def test_repository_root_fsync_failure_is_pre_arm_and_retryable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="fmsr1-root-fsync-") as directory:
            repo_root = Path(directory) / "repo"
            repo_root.mkdir()
            work_root = repo_root / admission.OFFICIAL_QUALIFICATION_ROOT.parent
            attempt_root = repo_root / admission.OFFICIAL_QUALIFICATION_ROOT

            def fail_root_fsync(_file_descriptor: int) -> None:
                raise OSError("injected repository-root fsync failure")

            with self.assert_refusal("ORDER_REFUSE"):
                with admission._official_qualification_root(
                    repo_root,
                    directory_fsync=fail_root_fsync,
                ):
                    pass

            self.assertTrue(work_root.is_dir())
            self.assertFalse(attempt_root.exists())
            with admission._official_qualification_root(repo_root) as (
                created_root,
                marker,
            ):
                self.assertEqual(created_root, attempt_root.resolve(strict=True))
                self.assertEqual(marker["attempt_state"], "armed_and_consumed")

    def test_work_root_fsync_failure_leaves_fail_closed_pending_reservation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="fmsr1-work-fsync-") as directory:
            repo_root = Path(directory) / "repo"
            repo_root.mkdir()
            attempt_root = repo_root / admission.OFFICIAL_QUALIFICATION_ROOT
            calls = 0

            def fail_work_fsync(file_descriptor: int) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected work-root fsync failure")
                os.fsync(file_descriptor)

            with self.assertRaises(admission.FMSR1AdmissionRefusal) as caught:
                with admission._official_qualification_root(
                    repo_root,
                    directory_fsync=fail_work_fsync,
                ):
                    pass

            self.assertEqual(caught.exception.route, "ORDER_REFUSE")
            self.assertIn("before arming", caught.exception.safe_reason)
            self.assertTrue(attempt_root.is_dir())
            self.assertFalse((attempt_root / "consumed.json").exists())
            with self.assert_refusal("ORDER_REFUSE"):
                with admission._official_qualification_root(repo_root):
                    pass

    def test_work_root_symlink_or_non_directory_refuses_pre_arm(self) -> None:
        for root_kind in ("symlink", "file"):
            with self.subTest(root_kind=root_kind), tempfile.TemporaryDirectory(
                prefix="fmsr1-work-types-"
            ) as directory:
                parent = Path(directory)
                repo_root = parent / "repo"
                repo_root.mkdir()
                work_root = repo_root / admission.OFFICIAL_QUALIFICATION_ROOT.parent
                if root_kind == "symlink":
                    target = parent / "outside-work"
                    target.mkdir()
                    work_root.symlink_to(target, target_is_directory=True)
                else:
                    work_root.write_bytes(b"generated")

                with (
                    self.assert_refusal("ORDER_REFUSE"),
                    admission._official_qualification_root(repo_root),
                ):
                    pass
                self.assertFalse(
                    (work_root / admission.OFFICIAL_QUALIFICATION_ROOT.name).exists()
                )

    def test_marker_rejects_changed_attempt_directory_identity(self) -> None:
        with admission._qualification_temp_root(
            "fmsr1-attempt-identity-"
        ) as attempt_root:
            identity = os.lstat(attempt_root)
            wrong_identity = (identity.st_dev, identity.st_ino + 1)

            with self.assert_refusal("ORDER_REFUSE"):
                admission.create_consumed_marker(
                    attempt_root,
                    self.marker_bytes(),
                    expected_stage="OFFICIAL_GENERATED_QUALIFICATION",
                    expected_parent_identity=wrong_identity,
                )
            self.assertFalse((attempt_root / "consumed.json").exists())

    def test_official_root_binds_marker_to_created_attempt_identity(self) -> None:
        original_create = admission.create_consumed_marker
        observed_identity: list[tuple[int, int]] = []

        def checked_create(
            parent: str | Path,
            marker_bytes: bytes,
            *,
            expected_stage: str,
            expected_parent_identity: tuple[int, int] | None = None,
            file_fsync: object = os.fsync,
            directory_fsync: object = os.fsync,
        ) -> dict[str, object]:
            self.assertIsNotNone(expected_parent_identity)
            parent_info = os.lstat(parent)
            actual_identity = (parent_info.st_dev, parent_info.st_ino)
            self.assertEqual(expected_parent_identity, actual_identity)
            observed_identity.append(actual_identity)
            return original_create(
                parent,
                marker_bytes,
                expected_stage=expected_stage,
                expected_parent_identity=expected_parent_identity,
                file_fsync=file_fsync,
                directory_fsync=directory_fsync,
            )

        with tempfile.TemporaryDirectory(prefix="fmsr1-identity-bind-") as directory:
            repo_root = Path(directory) / "repo"
            repo_root.mkdir()
            with mock.patch.object(
                admission,
                "create_consumed_marker",
                side_effect=checked_create,
            ), admission._official_qualification_root(repo_root):
                pass
        self.assertEqual(len(observed_identity), 1)

    def test_pre_arm_refusals_do_not_create_official_root(self) -> None:
        cases = (
            (
                "contract",
                mock.patch.object(
                    admission,
                    "_load_contract",
                    side_effect=admission.FMSR1AdmissionRefusal(
                        "AUTHORITY_REFUSE", "injected contract refusal"
                    ),
                ),
                mock.patch.object(
                    admission,
                    "_load_implementation_activation",
                    return_value={},
                ),
                THREAD_ENVIRONMENT,
                "AUTHORITY_REFUSE",
            ),
            (
                "activation",
                mock.patch.object(admission, "_load_contract", return_value={}),
                mock.patch.object(
                    admission,
                    "_load_implementation_activation",
                    side_effect=admission.FMSR1AdmissionRefusal(
                        "AUTHORITY_REFUSE", "injected activation refusal"
                    ),
                ),
                THREAD_ENVIRONMENT,
                "AUTHORITY_REFUSE",
            ),
            (
                "thread_environment",
                mock.patch.object(admission, "_load_contract", return_value={}),
                mock.patch.object(
                    admission,
                    "_load_implementation_activation",
                    return_value={},
                ),
                {**THREAD_ENVIRONMENT, admission.THREAD_ENV_KEYS[0]: "2"},
                "RESOURCE_REFUSE",
            ),
        )

        for name, contract_patch, activation_patch, environ, route in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory(
                prefix="fmsr1-pre-arm-"
            ) as directory:
                repo_root = Path(directory) / "repo"
                repo_root.mkdir()
                with contract_patch, activation_patch, self.assert_refusal(route):
                    admission.run_generated_qualification(
                        repo_root,
                        environ=environ,
                    )
                self.assertFalse(
                    (repo_root / admission.OFFICIAL_QUALIFICATION_ROOT).exists()
                )
                self.assertFalse(
                    (
                        repo_root
                        / admission.OFFICIAL_QUALIFICATION_ROOT.parent
                    ).exists()
                )

    def test_post_arm_failure_remains_consumed_and_blocks_second_run(self) -> None:
        with tempfile.TemporaryDirectory(prefix="fmsr1-post-arm-") as directory:
            repo_root = Path(directory) / "repo"
            repo_root.mkdir()
            attempt_root = repo_root / admission.OFFICIAL_QUALIFICATION_ROOT

            with (
                mock.patch.object(admission, "_load_contract", return_value={}),
                mock.patch.object(
                    admission,
                    "_load_implementation_activation",
                    return_value={},
                ),
                mock.patch.object(
                    admission,
                    "_run_acceptance_replay",
                    side_effect=InjectedPostArmFailure("generated post-arm fault"),
                ) as replay,
            ):
                with self.assertRaises(InjectedPostArmFailure):
                    admission.run_generated_qualification(
                        repo_root,
                        environ=THREAD_ENVIRONMENT,
                    )

                self.assertTrue(attempt_root.is_dir())
                self.assertTrue((attempt_root / "consumed.json").is_file())

                with self.assert_refusal("ORDER_REFUSE"):
                    admission.run_generated_qualification(
                        repo_root,
                        environ=THREAD_ENVIRONMENT,
                    )
                self.assertEqual(replay.call_count, 1)


if __name__ == "__main__":
    unittest.main()
