from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover - omp-config runs on POSIX hosts
    fcntl = None


POLICY_PATH = Path(__file__).resolve().parent.parent / "global" / "optmem-policy.json"
POLICY_FILE_MODE = 0o644
DIRECTORY_MODE = 0o700
FILE_MODE = 0o600
MEMO_MODE = 0o700


class OptMemError(RuntimeError):
    """A fail-closed OptMem administration error."""


class MissingInstallation(OptMemError):
    pass


class HashMismatch(OptMemError):
    pass


@dataclass(frozen=True)
class OptMemPolicy:
    repository: str
    commit: str
    url: str
    sha256: str
    installation_schema: str
    backup_schema: str
    log_record_bytes: int
    tree_record_bytes: int

@dataclass(frozen=True)
class OptMemPaths:
    root: Path
    memo: Path
    memory: Path
    log: Path
    tree: Path
    config: Path
    lock: Path
    receipt: Path
    backups: Path


@dataclass(frozen=True)
class _StoreInventory:
    records: dict[str, int]
    directories: tuple[Path, ...]
    files: tuple[Path, ...]


def paths(home: Path | None = None) -> OptMemPaths:
    selected_home = Path.home() if home is None else Path(home).expanduser()
    root = selected_home / ".optmem"
    memory = root / "memory"
    return OptMemPaths(
        root=root,
        memo=root / "memo",
        memory=memory,
        log=memory / "LOG.txt",
        tree=memory / "TREE",
        config=memory / "config",
        lock=memory / ".lock",
        receipt=root / "installation.json",
        backups=root / "backups",
    )


def _lexists(path: Path) -> bool:
    return os.path.lexists(path)


def _reject_symlink(path: Path, label: str) -> None:
    if path.is_symlink():
        raise OptMemError(f"{label} must not be a symlink: {path}")


def _require_directory(path: Path, label: str, *, create: bool = False) -> None:
    _reject_symlink(path, label)
    if not _lexists(path):
        if not create:
            raise MissingInstallation(f"missing {label}: {path}")
        path.mkdir(mode=DIRECTORY_MODE)
    if not path.is_dir():
        raise OptMemError(f"{label} must be a directory: {path}")
    _require_owner(path, label)


def _require_file(path: Path, label: str, *, missing_is_installation: bool = False) -> None:
    _reject_symlink(path, label)
    if not _lexists(path):
        if missing_is_installation:
            raise MissingInstallation(f"missing {label}: {path}")
        raise OptMemError(f"missing {label}: {path}")
    if not path.is_file():
        raise OptMemError(f"{label} must be a regular file: {path}")
    _require_owner(path, label)


def _mode(path: Path) -> int:
    return stat.S_IMODE(os.stat(path, follow_symlinks=False).st_mode)
def _require_owner(path: Path, label: str) -> None:
    owner = os.stat(path, follow_symlinks=False).st_uid
    if owner != os.getuid():
        raise OptMemError(f"{label} is not owned by the current user: {path}")



def _require_mode(path: Path, expected: int, label: str) -> None:
    actual = _mode(path)
    if actual != expected:
        raise OptMemError(f"{label} has mode {actual:04o}; expected {expected:04o}")

    _require_owner(path, label)

def _set_mode(path: Path, expected: int, label: str) -> None:
    _reject_symlink(path, label)
    os.chmod(path, expected)


def _load_policy() -> OptMemPolicy:
    _require_file(POLICY_PATH, "OptMem policy")
    _require_mode(POLICY_PATH, POLICY_FILE_MODE, "OptMem policy")
    try:
        document = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OptMemError(f"invalid OptMem policy: {error}") from error
    if not isinstance(document, dict) or set(document) != {"repository", "source", "schemas", "record_sizes"}:
        raise OptMemError("OptMem policy has an unsupported schema")
    repository = document["repository"]
    source = document["source"]
    schemas = document["schemas"]
    record_sizes = document["record_sizes"]
    if not isinstance(repository, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise OptMemError("OptMem policy repository is invalid")
    if not isinstance(source, dict) or set(source) != {"commit", "url", "sha256"}:
        raise OptMemError("OptMem policy source has an unsupported schema")
    commit = source["commit"]
    url = source["url"]
    sha256 = source["sha256"]
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise OptMemError("OptMem policy commit is invalid")
    expected_url = f"https://raw.githubusercontent.com/{repository}/{commit}/memo"
    if not isinstance(url, str) or url != expected_url:
        raise OptMemError("OptMem policy URL does not match its repository and commit")
    if not isinstance(sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise OptMemError("OptMem policy SHA-256 is invalid")
    if not isinstance(schemas, dict) or set(schemas) != {"installation", "backup"}:
        raise OptMemError("OptMem policy schemas have an unsupported schema")
    installation_schema = schemas["installation"]
    backup_schema = schemas["backup"]
    if (
        not isinstance(installation_schema, str)
        or not re.fullmatch(r"omp\.optmem\.installation\.v[0-9]+", installation_schema)
        or not isinstance(backup_schema, str)
        or not re.fullmatch(r"omp\.optmem\.backup\.v[0-9]+", backup_schema)
    ):
        raise OptMemError("OptMem policy schemas are invalid")
    if not isinstance(record_sizes, dict) or set(record_sizes) != {"log", "tree"}:
        raise OptMemError("OptMem policy record sizes have an unsupported schema")
    log_record_bytes = record_sizes["log"]
    tree_record_bytes = record_sizes["tree"]
    if (
        type(log_record_bytes) is not int
        or log_record_bytes <= 0
        or type(tree_record_bytes) is not int
        or tree_record_bytes <= 0
    ):
        raise OptMemError("OptMem policy record sizes must be positive integers")
    return OptMemPolicy(
        repository=repository,
        commit=commit,
        url=url,
        sha256=sha256,
        installation_schema=installation_schema,
        backup_schema=backup_schema,
        log_record_bytes=log_record_bytes,
        tree_record_bytes=tree_record_bytes,
    )

def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _authority_preflight(p: OptMemPaths) -> None:
    _reject_symlink(p.root, "OptMem authority root")
    if _lexists(p.root) and not p.root.is_dir():
        raise OptMemError(f"OptMem authority root must be a directory: {p.root}")
    if not _lexists(p.root):
        return
    for path, label in (
        (p.memo, "OptMem executable"),
        (p.memory, "OptMem store"),
        (p.receipt, "OptMem installation receipt"),
        (p.backups, "OptMem backup directory"),
    ):
        _reject_symlink(path, label)
    if p.memory.is_dir():
        for child in p.memory.rglob("*"):
            _reject_symlink(child, "OptMem store path")
    if p.backups.is_dir():
        for child in p.backups.rglob("*"):
            _reject_symlink(child, "OptMem backup path")


def _ensure_root(p: OptMemPaths) -> None:
    _authority_preflight(p)
    _require_directory(p.root, "OptMem authority root", create=True)
    _set_mode(p.root, DIRECTORY_MODE, "OptMem authority root")


def _inspect_store(p: OptMemPaths, policy: OptMemPolicy) -> _StoreInventory:
    _require_directory(p.memory, "OptMem store")
    _require_directory(p.tree, "OptMem TREE")
    _require_file(p.config, "OptMem config")
    _require_file(p.log, "OptMem LOG.txt")
    directories = [p.memory, p.tree]
    files = [p.config, p.log]
    log_size = p.log.stat().st_size
    if log_size % policy.log_record_bytes:
        raise OptMemError(
            f"OptMem LOG.txt is not aligned to {policy.log_record_bytes}-byte records"
        )
    tree_files = 0
    tree_records = 0
    for entry in sorted(p.tree.rglob("*")):
        _reject_symlink(entry, "OptMem TREE path")
        if entry.is_dir():
            _require_owner(entry, "OptMem TREE directory")
            directories.append(entry)
            continue
        if not entry.is_file():
            raise OptMemError(f"OptMem TREE contains unsupported path: {entry}")
        _require_owner(entry, "OptMem TREE file")
        size = entry.stat().st_size
        if size % policy.tree_record_bytes:
            raise OptMemError(
                f"OptMem TREE file {entry.name} is not aligned to {policy.tree_record_bytes}-byte records"
            )
        files.append(entry)
        tree_files += 1
        tree_records += size // policy.tree_record_bytes
    if _lexists(p.lock):
        _require_file(p.lock, "OptMem store lock")
        files.append(p.lock)
    for child in p.memory.iterdir():
        if child.name not in {"config", "LOG.txt", "TREE", ".lock"}:
            raise OptMemError(f"unexpected OptMem store path: {child.name}")
    return _StoreInventory(
        records={
            "log_records": log_size // policy.log_record_bytes,
            "tree_files": tree_files,
            "tree_records": tree_records,
        },
        directories=tuple(directories),
        files=tuple(files),
    )


def _verify_store(p: OptMemPaths, policy: OptMemPolicy) -> dict[str, int]:
    inventory = _inspect_store(p, policy)
    for directory in inventory.directories:
        _require_mode(directory, DIRECTORY_MODE, "OptMem store directory")
    for file in inventory.files:
        _require_mode(file, FILE_MODE, "OptMem store file")
    return inventory.records


def _normalize_store_permissions(inventory: _StoreInventory) -> None:
    for directory in inventory.directories:
        _set_mode(directory, DIRECTORY_MODE, "OptMem store directory")
    for file in inventory.files:
        _set_mode(file, FILE_MODE, "OptMem store file")


def _verify_backup_permissions(p: OptMemPaths) -> None:
    for entry in sorted(p.backups.rglob("*")):
        _reject_symlink(entry, "OptMem backup path")
        if entry.is_dir():
            _require_mode(entry, DIRECTORY_MODE, "OptMem backup directory")
        elif entry.is_file():
            expected = (
                MEMO_MODE
                if entry.name == "memo" and entry.parent.parent == p.backups
                else FILE_MODE
            )
            _require_mode(entry, expected, "OptMem backup file")
        else:
            raise OptMemError(f"OptMem backup contains unsupported path: {entry}")


def _read_receipt(p: OptMemPaths, policy: OptMemPolicy) -> dict[str, str]:
    _require_file(p.receipt, "OptMem installation receipt", missing_is_installation=True)
    _require_mode(p.receipt, FILE_MODE, "OptMem installation receipt")
    try:
        document = json.loads(p.receipt.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OptMemError(f"invalid OptMem installation receipt: {error}") from error
    expected_keys = {
        "schema",
        "repository",
        "commit",
        "url",
        "sha256",
        "installed_at",
        "installer",
    }
    if not isinstance(document, dict) or set(document) != expected_keys:
        raise OptMemError("OptMem installation receipt has an unsupported schema")
    if any(not isinstance(value, str) or not value for value in document.values()):
        raise OptMemError("OptMem installation receipt fields must be non-empty strings")
    if document["schema"] != policy.installation_schema:
        raise OptMemError(
            f"OptMem installation receipt schema must be {policy.installation_schema}"
        )
    if document["repository"] != policy.repository:
        raise OptMemError("OptMem installation receipt names an unexpected repository")
    if document["commit"] != policy.commit:
        raise OptMemError("OptMem installation receipt names an unexpected commit")
    if document["url"] != policy.url:
        raise OptMemError("OptMem installation receipt names an unexpected URL")
    if document["sha256"] != policy.sha256:
        raise OptMemError("OptMem installation receipt names an unexpected SHA-256")
    if document["installer"] != "omp-config":
        raise OptMemError("OptMem installation receipt names an unexpected installer")
    try:
        datetime.fromisoformat(document["installed_at"].replace("Z", "+00:00"))
    except ValueError as error:
        raise OptMemError("OptMem installation receipt has an invalid installed_at") from error
    return document


def verify_installation(home: Path | None = None) -> dict[str, object]:
    policy = _load_policy()
    p = paths(home)
    _authority_preflight(p)
    _require_directory(p.root, "OptMem authority root")
    _require_mode(p.root, DIRECTORY_MODE, "OptMem authority root")
    _require_file(p.memo, "OptMem executable", missing_is_installation=True)
    _require_mode(p.memo, MEMO_MODE, "OptMem executable")
    memo_hash = _sha256_file(p.memo)
    if memo_hash != policy.sha256:
        raise HashMismatch("installed OptMem executable does not match the pinned SHA-256")
    receipt = _read_receipt(p, policy)
    records = _verify_store(p, policy)
    _require_directory(p.backups, "OptMem backup directory", create=False)
    _require_mode(p.backups, DIRECTORY_MODE, "OptMem backup directory")
    _verify_backup_permissions(p)
    return {
        "schema": policy.installation_schema,
        "root": str(p.root),
        "memo": str(p.memo),
        "receipt": str(p.receipt),
        "commit": receipt["commit"],
        "sha256": memo_hash,
        "records": records,
    }




def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def _receipt(policy: OptMemPolicy) -> dict[str, str]:
    return {
        "schema": policy.installation_schema,
        "repository": policy.repository,
        "commit": policy.commit,
        "url": policy.url,
        "sha256": policy.sha256,
        "installed_at": _now(),
        "installer": "omp-config",
    }


def _write_bytes_atomic(path: Path, data: bytes, mode: int, label: str) -> None:
    _reject_symlink(path, label)
    if not path.parent.is_dir():
        raise OptMemError(f"missing parent for {label}: {path.parent}")
    _reject_symlink(path.parent, f"{label} parent")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{path.name}.", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        _set_mode(temporary, mode, f"temporary {label}")
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _write_receipt(p: OptMemPaths, receipt: dict[str, str]) -> None:
    encoded = (json.dumps(receipt, sort_keys=True, indent=2) + "\n").encode("utf-8")
    _write_bytes_atomic(p.receipt, encoded, FILE_MODE, "OptMem installation receipt")


def _fetch_memo(p: OptMemPaths, policy: OptMemPolicy) -> Path:
    _authority_preflight(p)
    parent = p.root if p.root.is_dir() else p.root.parent
    if not parent.is_dir():
        raise OptMemError(f"missing OptMem download parent: {parent}")
    _reject_symlink(parent, "OptMem download parent")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=".memo-download-", dir=parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            try:
                response = urllib.request.urlopen(policy.url, timeout=30)
            except OSError as error:
                raise OptMemError(f"cannot fetch pinned OptMem memo: {error}") from error
            try:
                resolved = getattr(response, "geturl", lambda: policy.url)()
                if resolved != policy.url:
                    raise OptMemError("pinned OptMem fetch redirected away from its commit URL")
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
            finally:
                response.close()
            handle.flush()
            os.fsync(handle.fileno())
        digest = _sha256_file(temporary)
        if digest != policy.sha256:
            raise HashMismatch("downloaded OptMem memo does not match the pinned SHA-256")
        _set_mode(temporary, MEMO_MODE, "downloaded OptMem memo")
        return temporary
    except Exception:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise


def _run_memo(path: Path, args: list[str], memory: Path, *, marker: str | None = None) -> None:
    environment = os.environ.copy()
    environment["MEMORY_DIR"] = str(memory)
    previous_umask = os.umask(0o077)
    try:
        try:
            result = subprocess.run(
                [str(path), *args],
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise OptMemError(
                f"OptMem command {' '.join(args)} failed: {type(error).__name__}"
            ) from error
        if result.returncode:
            raise OptMemError(
                f"OptMem command {' '.join(args)} failed with exit {result.returncode}"
            )
        if marker is not None and marker.encode("utf-8") not in result.stdout:
            raise OptMemError(f"OptMem command {' '.join(args)} omitted its success marker")
    finally:
        os.umask(previous_umask)


def _replace_memo(p: OptMemPaths, candidate: Path) -> None:
    _reject_symlink(p.memo, "OptMem executable")
    _set_mode(candidate, MEMO_MODE, "candidate OptMem executable")
    os.replace(candidate, p.memo)
    _fsync_directory(p.root)


def _restore_file(path: Path, data: bytes, mode: int, label: str) -> None:
    _write_bytes_atomic(path, data, mode, label)


def install(home: Path | None = None) -> dict[str, object]:
    """Install the pinned executable and initialize only a missing identity."""
    policy = _load_policy()
    previous_umask = os.umask(0o077)
    p = paths(home)
    old_root_exists = _lexists(p.root)
    old_root_mode = _mode(p.root) if old_root_exists and not p.root.is_symlink() else None
    old_memory_exists = _lexists(p.memory)
    old_memory_mode = _mode(p.memory) if old_memory_exists and not p.memory.is_symlink() else None
    old_memo = p.memo.read_bytes() if p.memo.is_file() and not p.memo.is_symlink() else None
    old_memo_mode = _mode(p.memo) if p.memo.is_file() and not p.memo.is_symlink() else None
    old_receipt = p.receipt.read_bytes() if p.receipt.is_file() and not p.receipt.is_symlink() else None
    old_backups_exists = _lexists(p.backups)
    old_backups_mode = _mode(p.backups) if old_backups_exists and not p.backups.is_symlink() else None
    old_receipt_mode = _mode(p.receipt) if p.receipt.is_file() and not p.receipt.is_symlink() else None
    candidate: Path | None = None
    identity_missing = not old_memory_exists
    try:
        candidate = _fetch_memo(p, policy)
        _ensure_root(p)
        if old_memory_exists:
            _require_directory(p.memory, "OptMem store")
        else:
            _reject_symlink(p.memory, "OptMem store")
            _run_memo(candidate, ["init"], p.memory)
        _require_directory(p.memory, "OptMem store")
        _set_mode(p.memory, DIRECTORY_MODE, "OptMem store")
        _require_directory(p.backups, "OptMem backup directory", create=True)
        _set_mode(p.backups, DIRECTORY_MODE, "OptMem backup directory")
        _replace_memo(p, candidate)
        candidate = None
        _write_receipt(p, _receipt(policy))
        return verify_installation(home)
    except Exception:
        if candidate is not None:
            candidate.unlink(missing_ok=True)
        if p.root.is_dir():
            if old_memo is None:
                p.memo.unlink(missing_ok=True)
            else:
                _restore_file(p.memo, old_memo, old_memo_mode or MEMO_MODE, "OptMem executable rollback")
            if old_receipt is None:
                p.receipt.unlink(missing_ok=True)
            else:
                _restore_file(
                    p.receipt,
                    old_receipt,
                    old_receipt_mode or FILE_MODE,
                    "OptMem installation receipt rollback",
                )
            if identity_missing and not old_memory_exists and p.memory.is_dir():
                shutil.rmtree(p.memory)
            if not old_backups_exists and p.backups.is_dir():
                shutil.rmtree(p.backups)
            if old_backups_mode is not None and p.backups.is_dir():
                _set_mode(p.backups, old_backups_mode, "OptMem backup rollback")
            if old_memory_mode is not None and p.memory.is_dir():
                _set_mode(p.memory, old_memory_mode, "OptMem store rollback")
            if old_root_mode is not None and p.root.is_dir():
                _set_mode(p.root, old_root_mode, "OptMem authority root rollback")
            if not old_root_exists and p.root.is_dir():
                shutil.rmtree(p.root)
        raise
    finally:
        if candidate is not None:
            candidate.unlink(missing_ok=True)
        os.umask(previous_umask)


@contextmanager
def _store_lock(p: OptMemPaths) -> Iterator[None]:
    existed = _lexists(p.lock)
    _reject_symlink(p.lock, "OptMem store lock")
    try:
        handle = p.lock.open("a+b")
    except OSError as error:
        raise OptMemError(f"cannot open OptMem store lock: {error}") from error
    failed = False
    try:
        _set_mode(p.lock, FILE_MODE, "OptMem store lock")
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    except Exception:
        failed = True
        raise
    finally:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()
        if failed and not existed:
            p.lock.unlink(missing_ok=True)


def _copy_file(source: Path, destination: Path, mode: int, label: str) -> None:
    _reject_symlink(source, label)
    _require_file(source, label)
    _reject_symlink(destination, f"backup destination {destination}")
    destination.parent.mkdir(mode=DIRECTORY_MODE, parents=True, exist_ok=True)
    _reject_symlink(destination.parent, "backup destination parent")
    with source.open("rb") as src, destination.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)
        dst.flush()
        os.fsync(dst.fileno())
    _set_mode(destination, mode, f"backup {label}")


def _backup_stamp(root: Path) -> tuple[str, Path, Path]:
    base = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for suffix in range(1000):
        name = base if suffix == 0 else f"{base}-{suffix:03d}"
        final = root / name
        staging = root / f".{name}.staging"
        if not _lexists(final) and not _lexists(staging):
            return name, staging, final
    raise OptMemError("cannot allocate a unique OptMem backup name")


def backup(home: Path | None = None) -> Path:
    """Create a verified, hashed, atomic whole-store snapshot."""
    policy = _load_policy()
    p = paths(home)
    _authority_preflight(p)
    inventory = _inspect_store(p, policy)
    _normalize_store_permissions(inventory)
    verify_installation(home)
    _require_directory(p.backups, "OptMem backup directory", create=True)
    _set_mode(p.backups, DIRECTORY_MODE, "OptMem backup directory")
    with _store_lock(p):
        records = _verify_store(p, policy)
        name, staging, final = _backup_stamp(p.backups)
        staging.mkdir(mode=DIRECTORY_MODE)
        try:
            _set_mode(staging, DIRECTORY_MODE, "OptMem backup staging")
            files: list[dict[str, object]] = []

            def copy_record(source: Path, relative: Path, mode: int, label: str) -> None:
                destination = staging / relative
                _copy_file(source, destination, mode, label)
                files.append(
                    {
                        "path": relative.as_posix(),
                        "size": destination.stat().st_size,
                        "sha256": _sha256_file(destination),
                    }
                )

            copy_record(p.memo, Path("memo"), MEMO_MODE, "OptMem executable")
            copy_record(p.receipt, Path("installation.json"), FILE_MODE, "OptMem installation receipt")
            copy_record(p.config, Path("memory/config"), FILE_MODE, "OptMem config")
            copy_record(p.log, Path("memory/LOG.txt"), FILE_MODE, "OptMem LOG.txt")
            (staging / "memory/TREE").mkdir(mode=DIRECTORY_MODE, parents=True)
            _set_mode(staging / "memory", DIRECTORY_MODE, "OptMem backup memory")
            _set_mode(staging / "memory/TREE", DIRECTORY_MODE, "OptMem backup TREE")
            for source in sorted(p.tree.rglob("*")):
                if source.is_dir():
                    relative = Path("memory/TREE") / source.relative_to(p.tree)
                    (staging / relative).mkdir(mode=DIRECTORY_MODE, parents=True, exist_ok=True)
                    _set_mode(staging / relative, DIRECTORY_MODE, "OptMem backup TREE directory")
                else:
                    relative = Path("memory/TREE") / source.relative_to(p.tree)
                    copy_record(source, relative, FILE_MODE, "OptMem TREE file")
            manifest = {
                "schema": policy.backup_schema,
                "created_at": _now(),
                "commit": policy.commit,
                "sha256": policy.sha256,
                "records": records,
                "files": files,
            }
            _write_bytes_atomic(
                staging / "manifest.json",
                (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8"),
                FILE_MODE,
                "OptMem backup manifest",
            )
            for directory in sorted(
                (entry for entry in staging.rglob("*") if entry.is_dir()),
                key=lambda entry: len(entry.parts),
                reverse=True,
            ):
                _fsync_directory(directory)
            _fsync_directory(staging)
            os.replace(staging, final)
            _fsync_directory(p.backups)
            return final
        except Exception:
            if staging.exists() and not staging.is_symlink():
                shutil.rmtree(staging)
            raise


def _probe_updated_memo(p: OptMemPaths) -> None:
    _run_memo(p.memo, ["config"], p.memory, marker="WAKE_LINES")
    _run_memo(p.memo, ["wake"], p.memory, marker="You are awake.")


def update(home: Path | None = None) -> dict[str, object]:
    """Refresh the same immutable pin, with a verified rollback backup."""
    policy = _load_policy()
    p = paths(home)
    _authority_preflight(p)
    inventory = _inspect_store(p, policy)
    _normalize_store_permissions(inventory)
    verify_installation(home)
    old_memo = p.memo.read_bytes()
    old_receipt = p.receipt.read_bytes()
    candidate: Path | None = None
    replaced = False
    try:
        candidate = _fetch_memo(p, policy)
        backup_path = backup(home)
        replaced = True
        _replace_memo(p, candidate)
        candidate = None
        _probe_updated_memo(p)
        _write_receipt(p, _receipt(policy))
        verified = verify_installation(home)
        verified["backup"] = str(backup_path)
        return verified
    except Exception:
        if candidate is not None:
            candidate.unlink(missing_ok=True)
        if replaced:
            _restore_file(p.memo, old_memo, MEMO_MODE, "OptMem executable rollback")
            _restore_file(p.receipt, old_receipt, FILE_MODE, "OptMem installation receipt rollback")
        raise
    finally:
        if candidate is not None:
            candidate.unlink(missing_ok=True)

def ensure_verified(home: Path | None = None) -> dict[str, object]:
    """Verify an existing dependency, installing only when authority is absent."""
    try:
        return verify_installation(home)
    except MissingInstallation:
        return install(home)


