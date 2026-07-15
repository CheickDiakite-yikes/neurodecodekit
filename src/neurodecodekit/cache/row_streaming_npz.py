"""Bounded sequential row access for numeric NPY members inside NPZ archives."""

from __future__ import annotations

import hashlib
import json
import math
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


class RowStreamingNPZError(ValueError):
    """Raised when an archive cannot satisfy the bounded row-read contract."""


@dataclass(frozen=True)
class NPYMemberHeader:
    """Header and ZIP-directory facts available before array values are read."""

    member_name: str
    npy_version: tuple[int, int]
    shape: tuple[int, ...]
    dtype: str
    fortran_order: bool
    row_count: int
    row_bytes: int
    uncompressed_bytes: int
    compressed_bytes: int
    compression_type: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StreamedRows:
    """Selected rows plus an explicit traversal ledger."""

    member_name: str
    requested_indices: tuple[int, ...]
    values: Any
    header: NPYMemberHeader
    header_reads: int
    member_streams: int
    physical_rows_traversed: int
    opaque_excluded_rows_traversed: int
    delivered_rows: int
    uncompressed_value_bytes_read: int
    delivered_value_bytes: int
    reusable_buffer_bytes: int
    reusable_buffer_overwrites: int

    def ledger(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("values")
        payload["header"] = self.header.to_dict()
        return payload


def inspect_npz_members(
    path: str | Path,
    *,
    member_names: Iterable[str] | None = None,
) -> dict[str, NPYMemberHeader]:
    """Inspect ZIP metadata and NPY headers without loading array values."""

    archive = Path(path)
    requested = None if member_names is None else tuple(_member_name(v) for v in member_names)
    with zipfile.ZipFile(archive, mode="r") as bundle:
        available = {info.filename: info for info in bundle.infolist()}
        names = tuple(available) if requested is None else requested
        missing = sorted(set(names) - set(available))
        if missing:
            raise RowStreamingNPZError(f"NPZ archive is missing members: {missing}")
        headers = {}
        for name in names:
            info = available[name]
            with bundle.open(info, mode="r") as stream:
                headers[name] = _read_header(stream, info)
    return headers


def stream_npz_rows(
    path: str | Path,
    member_name: str,
    row_indices: Iterable[int],
    *,
    expected_shape: Iterable[int] | None = None,
    expected_dtype: str | None = None,
    maximum_row_bytes: int = 16 * 1024 * 1024,
) -> StreamedRows:
    """Sequentially traverse one NPY member and return only requested rows.

    Deflated NPZ members do not support physical row-level random access. This
    function therefore makes one forward member traversal, copies only allowed
    rows into the result, and records every excluded row crossed on the way.
    """

    np, _format = _require_numpy()
    archive = Path(path)
    name = _member_name(member_name)
    requested = tuple(int(value) for value in row_indices)
    if not requested:
        raise RowStreamingNPZError("row_indices must contain at least one row")
    if len(requested) != len(set(requested)):
        raise RowStreamingNPZError("row_indices must not repeat a row")
    if any(value < 0 for value in requested):
        raise RowStreamingNPZError("row_indices must be nonnegative")
    if maximum_row_bytes < 1:
        raise RowStreamingNPZError("maximum_row_bytes must be positive")

    with zipfile.ZipFile(archive, mode="r") as bundle:
        try:
            info = bundle.getinfo(name)
        except KeyError as exc:
            raise RowStreamingNPZError(f"NPZ archive is missing member: {name}") from exc
        with bundle.open(info, mode="r") as stream:
            header = _read_header(stream, info)
            if not header.shape:
                raise RowStreamingNPZError(f"{name} is scalar and cannot be row-streamed")
            if expected_shape is not None and header.shape != tuple(int(v) for v in expected_shape):
                raise RowStreamingNPZError(
                    f"{name} shape mismatch: {header.shape} != {tuple(expected_shape)}"
                )
            if expected_dtype is not None and np.dtype(header.dtype) != np.dtype(expected_dtype):
                raise RowStreamingNPZError(
                    f"{name} dtype mismatch: {header.dtype} != {np.dtype(expected_dtype)}"
                )
            if max(requested) >= header.row_count:
                raise RowStreamingNPZError(f"{name} row index exceeds row count {header.row_count}")
            if header.row_bytes > maximum_row_bytes:
                raise RowStreamingNPZError(
                    f"{name} row requires {header.row_bytes} bytes, above cap {maximum_row_bytes}"
                )

            selected_set = set(requested)
            stop_after = max(requested)
            selected: dict[int, Any] = {}
            buffer = bytearray(header.row_bytes)
            overwrites = 0
            traversed = 0
            excluded = 0
            value_bytes_read = 0
            dtype = np.dtype(header.dtype)
            row_shape = header.shape[1:]
            for row_index in range(stop_after + 1):
                _read_exact_into(stream, buffer)
                traversed += 1
                value_bytes_read += len(buffer)
                if row_index in selected_set:
                    row = np.frombuffer(buffer, dtype=dtype).copy()
                    selected[row_index] = row.reshape(row_shape)
                else:
                    excluded += 1
                buffer[:] = b"\0" * len(buffer)
                overwrites += 1

    values = np.stack([selected[index] for index in requested], axis=0)
    return StreamedRows(
        member_name=name,
        requested_indices=requested,
        values=values,
        header=header,
        header_reads=1,
        member_streams=1,
        physical_rows_traversed=traversed,
        opaque_excluded_rows_traversed=excluded,
        delivered_rows=len(requested),
        uncompressed_value_bytes_read=value_bytes_read,
        delivered_value_bytes=int(values.nbytes),
        reusable_buffer_bytes=len(buffer),
        reusable_buffer_overwrites=overwrites,
    )


def sha256_file_once(
    path: str | Path,
    *,
    expected_bytes: int | None = None,
    expected_sha256: str | None = None,
    chunk_bytes: int = 1024 * 1024,
) -> dict[str, Any]:
    """Hash one file in a single forward pass and verify optional bindings."""

    source = Path(path)
    if chunk_bytes < 1:
        raise ValueError("chunk_bytes must be positive")
    stat_bytes = int(source.stat().st_size)
    if expected_bytes is not None and stat_bytes != int(expected_bytes):
        raise RowStreamingNPZError(f"file byte mismatch: {stat_bytes} != {int(expected_bytes)}")
    digest = hashlib.sha256()
    bytes_read = 0
    with source.open("rb") as stream:
        while True:
            chunk = stream.read(chunk_bytes)
            if not chunk:
                break
            digest.update(chunk)
            bytes_read += len(chunk)
    actual = digest.hexdigest()
    if bytes_read != stat_bytes:
        raise RowStreamingNPZError(
            f"hash pass read {bytes_read} bytes but stat reported {stat_bytes}"
        )
    if expected_sha256 is not None and actual != str(expected_sha256):
        raise RowStreamingNPZError(f"file SHA-256 mismatch: {actual} != {expected_sha256}")
    return {
        "path": str(source),
        "bytes": stat_bytes,
        "bytes_read": bytes_read,
        "sha256": actual,
        "hash_passes": 1,
    }


def read_npz_json_scalar(
    path: str | Path,
    member_name: str = "metadata",
    *,
    maximum_uncompressed_bytes: int = 1024 * 1024,
) -> dict[str, Any]:
    """Read one bounded scalar JSON NPY member without enabling pickle."""

    np, fmt = _require_numpy()
    name = _member_name(member_name)
    with zipfile.ZipFile(Path(path), mode="r") as bundle:
        try:
            info = bundle.getinfo(name)
        except KeyError as exc:
            raise RowStreamingNPZError(f"NPZ archive is missing member: {name}") from exc
        if info.file_size > maximum_uncompressed_bytes:
            raise RowStreamingNPZError(
                f"{name} exceeds scalar metadata cap {maximum_uncompressed_bytes}"
            )
        with bundle.open(info, mode="r") as stream:
            try:
                value = fmt.read_array(
                    stream,
                    allow_pickle=False,
                    max_header_size=10_000,
                )
            except (EOFError, ValueError) as exc:
                raise RowStreamingNPZError(f"invalid scalar NPY member: {name}") from exc
    if value.shape != () or value.dtype.hasobject:
        raise RowStreamingNPZError(f"{name} must be one non-object scalar")
    raw = value.item()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    if not isinstance(raw, str):
        raise RowStreamingNPZError(f"{name} must contain JSON text")
    decoded = json.loads(raw)
    if not isinstance(decoded, dict):
        raise RowStreamingNPZError(f"{name} JSON must decode to an object")
    return decoded


def _read_header(stream, info: zipfile.ZipInfo) -> NPYMemberHeader:
    np, fmt = _require_numpy()
    try:
        version = tuple(int(value) for value in fmt.read_magic(stream))
        if version == (1, 0):
            shape, fortran_order, dtype = fmt.read_array_header_1_0(stream)
        elif version == (2, 0):
            shape, fortran_order, dtype = fmt.read_array_header_2_0(stream)
        elif version == (3, 0):
            shape, fortran_order, dtype = fmt._read_array_header(stream, version)
        else:
            raise RowStreamingNPZError(f"unsupported NPY version {version}")
    except (EOFError, ValueError) as exc:
        raise RowStreamingNPZError(f"invalid NPY header in {info.filename}") from exc
    dtype = np.dtype(dtype)
    shape = tuple(int(value) for value in shape)
    if any(value < 1 for value in shape):
        raise RowStreamingNPZError(f"{info.filename} must have positive dimensions")
    if dtype.hasobject:
        raise RowStreamingNPZError(f"{info.filename} uses forbidden object dtype")
    if bool(fortran_order):
        raise RowStreamingNPZError(f"{info.filename} uses unsupported Fortran order")
    row_elements = math.prod(shape[1:]) if shape else 1
    row_bytes = int(row_elements * dtype.itemsize)
    if row_bytes < 1:
        raise RowStreamingNPZError(f"{info.filename} has an invalid row byte size")
    return NPYMemberHeader(
        member_name=info.filename,
        npy_version=version,
        shape=shape,
        dtype=str(dtype),
        fortran_order=False,
        row_count=shape[0] if shape else 0,
        row_bytes=row_bytes,
        uncompressed_bytes=int(info.file_size),
        compressed_bytes=int(info.compress_size),
        compression_type=int(info.compress_type),
    )


def _read_exact_into(stream, buffer: bytearray) -> None:
    view = memoryview(buffer)
    offset = 0
    while offset < len(buffer):
        count = stream.readinto(view[offset:])
        if count is None:
            chunk = stream.read(len(buffer) - offset)
            count = len(chunk)
            view[offset : offset + count] = chunk
        if count == 0:
            raise RowStreamingNPZError("NPY member ended before a complete row was read")
        offset += int(count)


def _member_name(value: str) -> str:
    name = str(value)
    return name if name.endswith(".npy") else f"{name}.npy"


def _require_numpy():
    try:
        import numpy as np
        from numpy.lib import format as fmt
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Row-streaming NPZ access requires NumPy: `pip install numpy`.") from exc
    return np, fmt
