#!/usr/bin/env python3
"""Descriptor-anchored filesystem operations for the local Artifact helpers.

Python does not expose ``dir_fd`` operations on every supported macOS build.
This module keeps one fail-closed interface and uses libc's *at(2) calls when
the standard library cannot provide it.  Every traversed component is opened
relative to a held directory descriptor with ``O_NOFOLLOW``.
"""

import ctypes
import errno
import os
import secrets
import stat
import sys


DIRECTORY_FLAGS = (
    os.O_RDONLY
    | getattr(os, "O_DIRECTORY", 0)
    | getattr(os, "O_NOFOLLOW", 0)
    | getattr(os, "O_CLOEXEC", 0)
)
READ_FLAGS = (
    os.O_RDONLY
    | getattr(os, "O_NOFOLLOW", 0)
    | getattr(os, "O_CLOEXEC", 0)
    | getattr(os, "O_NONBLOCK", 0)
)
WRITE_FLAGS = (
    os.O_WRONLY
    | os.O_CREAT
    | os.O_EXCL
    | getattr(os, "O_NOFOLLOW", 0)
    | getattr(os, "O_CLOEXEC", 0)
)


def _component(name):
    if (
        not name
        or name in (".", "..")
        or os.path.sep in name
        or (os.path.altsep and os.path.altsep in name)
        or "\x00" in name
    ):
        raise ValueError(f"invalid path component: {name!r}")
    return name


def normalized_absolute(path):
    """Return an absolute lexical path without accepting arbitrary symlinks.

    Darwin exposes ``/tmp`` and ``/var`` as fixed root-owned compatibility
    aliases.  Normalize only those platform aliases; all later traversal is
    descriptor-relative and rejects every symlink.
    """
    value = os.path.abspath(os.path.expanduser(path))
    if sys.platform == "darwin":
        for alias, target in (("/tmp", "/private/tmp"), ("/var", "/private/var")):
            if value == alias or value.startswith(alias + os.path.sep):
                value = target + value[len(alias) :]
                break
    return value


_NATIVE_DIR_FD = os.open in os.supports_dir_fd
_NATIVE_LISTDIR_FD = os.listdir in os.supports_fd
_LIBC = None
if not _NATIVE_DIR_FD:
    try:
        _LIBC = ctypes.CDLL(None, use_errno=True)
        for symbol in ("openat", "mkdirat", "unlinkat"):
            if not hasattr(_LIBC, symbol):
                raise AttributeError(symbol)
        _LIBC.openat.restype = ctypes.c_int
        _LIBC.mkdirat.restype = ctypes.c_int
        _LIBC.unlinkat.restype = ctypes.c_int
    except (AttributeError, OSError) as err:
        raise RuntimeError(
            "Artifact requires descriptor-relative openat support on this platform"
        ) from err


class _DarwinDirent(ctypes.Structure):
    _fields_ = [
        ("d_ino", ctypes.c_uint64),
        ("d_seekoff", ctypes.c_uint64),
        ("d_reclen", ctypes.c_uint16),
        ("d_namlen", ctypes.c_uint16),
        ("d_type", ctypes.c_uint8),
        ("d_name", ctypes.c_char * 1024),
    ]


_DARWIN_D_NAME_SIZE = 1024


class _LinuxDirent(ctypes.Structure):
    _fields_ = [
        ("d_ino", ctypes.c_uint64),
        ("d_off", ctypes.c_int64),
        ("d_reclen", ctypes.c_uint16),
        ("d_type", ctypes.c_uint8),
        ("d_name", ctypes.c_char * 256),
    ]


_DIRENT = _DarwinDirent if sys.platform == "darwin" else _LinuxDirent
_DIR_LIBC = ctypes.CDLL(None, use_errno=True)
try:
    _DIR_LIBC.fdopendir.argtypes = [ctypes.c_int]
    _DIR_LIBC.fdopendir.restype = ctypes.c_void_p
    _READDIR = _DIR_LIBC.readdir
    _READDIR.argtypes = [ctypes.c_void_p]
    _READDIR.restype = ctypes.POINTER(_DIRENT)
    _DIR_LIBC.closedir.argtypes = [ctypes.c_void_p]
    _DIR_LIBC.closedir.restype = ctypes.c_int
except AttributeError as err:
    raise RuntimeError("Artifact requires fdopendir support") from err


def _raise_errno(name):
    value = ctypes.get_errno()
    raise OSError(value, os.strerror(value), name)


def open_at(directory_fd, name, flags, mode=0o666):
    name = _component(name)
    if _NATIVE_DIR_FD:
        return os.open(name, flags, mode, dir_fd=directory_fd)
    result = _LIBC.openat(
        ctypes.c_int(directory_fd),
        ctypes.c_char_p(os.fsencode(name)),
        ctypes.c_int(flags),
        ctypes.c_uint(mode),
    )
    if result < 0:
        _raise_errno(name)
    return result


def mkdir_at(directory_fd, name, mode=0o755):
    name = _component(name)
    if _NATIVE_DIR_FD:
        return os.mkdir(name, mode, dir_fd=directory_fd)
    result = _LIBC.mkdirat(
        ctypes.c_int(directory_fd),
        ctypes.c_char_p(os.fsencode(name)),
        ctypes.c_uint(mode),
    )
    if result < 0:
        _raise_errno(name)


def unlink_at(directory_fd, name):
    name = _component(name)
    if _NATIVE_DIR_FD:
        return os.unlink(name, dir_fd=directory_fd)
    result = _LIBC.unlinkat(
        ctypes.c_int(directory_fd), ctypes.c_char_p(os.fsencode(name)), ctypes.c_int(0)
    )
    if result < 0:
        _raise_errno(name)


def remove_directory_at(directory_fd, name):
    name = _component(name)
    if _NATIVE_DIR_FD:
        return os.rmdir(name, dir_fd=directory_fd)
    result = _LIBC.unlinkat(
        ctypes.c_int(directory_fd),
        ctypes.c_char_p(os.fsencode(name)),
        ctypes.c_int(0x0080 if sys.platform == "darwin" else 0x0200),
    )
    if result < 0:
        _raise_errno(name)


_RENAME_LIBC = ctypes.CDLL(None, use_errno=True)
if sys.platform == "darwin" and hasattr(_RENAME_LIBC, "renameatx_np"):
    _RENAME_WITH_FLAGS = _RENAME_LIBC.renameatx_np
    _RENAME_NOREPLACE = 0x00000004  # RENAME_EXCL
    _RENAME_EXCHANGE = 0x00000002  # RENAME_SWAP
elif sys.platform.startswith("linux") and hasattr(_RENAME_LIBC, "renameat2"):
    _RENAME_WITH_FLAGS = _RENAME_LIBC.renameat2
    _RENAME_NOREPLACE = 1
    _RENAME_EXCHANGE = 2
else:
    raise RuntimeError(
        "Artifact requires atomic no-replace and exchange rename support"
    )
_RENAME_WITH_FLAGS.restype = ctypes.c_int


def rename_at_with_flags(
    source_directory_fd, source, destination_directory_fd, destination, flags
):
    source = _component(source)
    destination = _component(destination)
    result = _RENAME_WITH_FLAGS(
        ctypes.c_int(source_directory_fd),
        ctypes.c_char_p(os.fsencode(source)),
        ctypes.c_int(destination_directory_fd),
        ctypes.c_char_p(os.fsencode(destination)),
        ctypes.c_uint(flags),
    )
    if result < 0:
        _raise_errno(destination)


def regular_identity_at(directory_fd, name, missing_ok=False):
    """Return one regular leaf's identity without following or blocking on it."""
    try:
        file_fd = open_at(directory_fd, name, READ_FLAGS)
    except FileNotFoundError:
        if missing_ok:
            return None
        raise
    except OSError as err:
        if err.errno == errno.ELOOP:
            raise ValueError(f"symlink leaf is not allowed: {name}") from err
        raise
    try:
        file_stat = os.fstat(file_fd)
        if not stat.S_ISREG(file_stat.st_mode):
            raise ValueError(f"not a regular file: {name}")
        return file_stat.st_dev, file_stat.st_ino
    finally:
        os.close(file_fd)


class AtomicWritePostCommitError(Exception):
    """The destination is installed, but durability or cleanup is unknown."""

    outcome = "COMMITTED/DURABILITY_UNKNOWN"

    def __init__(self, phase, cause, cleanup_error=None):
        self.phase = phase
        self.cause = cause
        self.cleanup_error = cleanup_error
        message = f"Artifact write outcome={self.outcome}; {phase} failed"
        if cleanup_error is not None:
            message += "; transaction cleanup also failed"
        super().__init__(message)


def guarded_replace(
    source_directory_fd, temporary, destination_directory_fd, name, expected_identity
):
    """Install a temporary regular file without replacing an unsafe leaf.

    An absent destination is installed with no-replace semantics.  An existing
    regular destination is atomically exchanged, then the displaced inode is
    checked against the identity observed before the write.  If that identity
    does not match, the exchange is an irrevocable crossed commit: the
    displaced leaf remains in the held transaction directory as recovery
    evidence and no rollback exchange is attempted.
    """
    if expected_identity is None:
        rename_at_with_flags(
            source_directory_fd,
            temporary,
            destination_directory_fd,
            name,
            _RENAME_NOREPLACE,
        )
        return

    rename_at_with_flags(
        source_directory_fd,
        temporary,
        destination_directory_fd,
        name,
        _RENAME_EXCHANGE,
    )
    try:
        displaced_identity = regular_identity_at(source_directory_fd, temporary)
        if displaced_identity != expected_identity:
            raise OSError(errno.ESTALE, "destination changed during write", name)
    except Exception as replacement_error:
        # The first exchange already installed the candidate at the public
        # destination.  Resolving the transaction pathname again and
        # exchanging it back creates a second attacker-controlled lookup
        # window, so the crossed commit must remain in place.
        raise AtomicWritePostCommitError(
            "destination rollback source validation", replacement_error
        ) from replacement_error


def _open_transaction_directory(directory_fd):
    """Create a private transaction directory and return its name and FD."""
    while True:
        name = f".artifact-txn-{os.getpid()}-{secrets.token_hex(16)}"
        try:
            mkdir_at(directory_fd, name, 0o700)
        except FileExistsError:
            continue
        try:
            return name, open_child_directory(directory_fd, name)
        except Exception:
            try:
                remove_directory_at(directory_fd, name)
            except OSError:
                pass
            raise


def open_directory(path, create=False):
    """Open an absolute directory without following any path component."""
    path = normalized_absolute(path)
    directory_fd = os.open(os.path.sep, DIRECTORY_FLAGS)
    try:
        for component in (part for part in path.split(os.path.sep) if part):
            try:
                child_fd = open_at(directory_fd, component, DIRECTORY_FLAGS)
            except FileNotFoundError:
                if not create:
                    raise
                try:
                    mkdir_at(directory_fd, component)
                except FileExistsError:
                    pass
                child_fd = open_at(directory_fd, component, DIRECTORY_FLAGS)
            os.close(directory_fd)
            directory_fd = child_fd
        if not stat.S_ISDIR(os.fstat(directory_fd).st_mode):
            raise NotADirectoryError(path)
        return directory_fd
    except Exception:
        os.close(directory_fd)
        raise


def open_child_directory(directory_fd, name, create=False):
    name = _component(name)
    try:
        child_fd = open_at(directory_fd, name, DIRECTORY_FLAGS)
    except FileNotFoundError:
        if not create:
            raise
        try:
            mkdir_at(directory_fd, name)
        except FileExistsError:
            pass
        child_fd = open_at(directory_fd, name, DIRECTORY_FLAGS)
    if not stat.S_ISDIR(os.fstat(child_fd).st_mode):
        os.close(child_fd)
        raise NotADirectoryError(name)
    return child_fd


def open_absolute_regular(path):
    """Open one absolute regular file through held, no-follow parent FDs."""
    path = normalized_absolute(path)
    parent, leaf = os.path.split(path)
    directory_fd = open_directory(parent)
    try:
        file_fd = open_at(directory_fd, leaf, READ_FLAGS)
    finally:
        os.close(directory_fd)
    if not stat.S_ISREG(os.fstat(file_fd).st_mode):
        os.close(file_fd)
        raise ValueError(f"not a regular file: {path}")
    return file_fd


def open_regular_at(directory_fd, name):
    file_fd = open_at(directory_fd, name, READ_FLAGS)
    if not stat.S_ISREG(os.fstat(file_fd).st_mode):
        os.close(file_fd)
        raise ValueError(f"not a regular file: {name}")
    return file_fd


def atomic_write_text(directory_fd, name, content):
    """Atomically replace one regular leaf and reject every other leaf type."""
    name = _component(name)
    expected_identity = regular_identity_at(directory_fd, name, missing_ok=True)
    transaction_name, transaction_fd = _open_transaction_directory(directory_fd)
    temporary = f"leaf-{secrets.token_hex(16)}"
    file_fd = None
    committed = False
    try:
        file_fd = open_at(transaction_fd, temporary, WRITE_FLAGS, 0o600)
        with os.fdopen(file_fd, "w", encoding="utf-8") as output:
            file_fd = None
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        try:
            guarded_replace(
                transaction_fd, temporary, directory_fd, name, expected_identity
            )
        except AtomicWritePostCommitError:
            # The exchange commit point was crossed but rollback could not be
            # proven. Preserve the private transaction directory as recovery
            # evidence and never run precommit cleanup against its old leaf.
            committed = True
            raise
        committed = True
        try:
            # The exchange/no-replace rename is the commit point.  A failed
            # directory sync therefore reports an installed leaf, not a
            # precommit write failure.
            os.fsync(directory_fd)
        except OSError as err:
            raise AtomicWritePostCommitError("directory fsync", err) from err
        if expected_identity is not None:
            try:
                # The displaced leaf is recovery evidence until the
                # transaction directory sync below proves its deletion
                # durable.
                unlink_at(transaction_fd, temporary)
            except OSError as err:
                raise AtomicWritePostCommitError(
                    "transaction leaf cleanup", err
                ) from err
        try:
            # The source leaf was removed from the transaction directory (or
            # moved out of it for a no-replace install), so sync that held
            # directory before closing it or removing its recovery evidence.
            os.fsync(transaction_fd)
        except OSError as err:
            raise AtomicWritePostCommitError(
                "transaction leaf cleanup fsync", err
            ) from err
        try:
            os.close(transaction_fd)
        except OSError as err:
            raise AtomicWritePostCommitError(
                "transaction descriptor cleanup", err
            ) from err
        else:
            transaction_fd = None
        recovery_name = f".artifact-recovery-{transaction_name}"
        try:
            # This marker is durable before the transaction directory is
            # removed.  If the following parent sync fails, the marker is
            # therefore still available for reconciliation.
            mkdir_at(directory_fd, recovery_name, 0o700)
        except OSError as err:
            raise AtomicWritePostCommitError(
                "recovery marker creation", err
            ) from err
        try:
            os.fsync(directory_fd)
        except OSError as err:
            raise AtomicWritePostCommitError(
                "recovery marker fsync", err
            ) from err
        try:
            remove_directory_at(directory_fd, transaction_name)
        except OSError as err:
            raise AtomicWritePostCommitError(
                "transaction directory cleanup", err
            ) from err
        try:
            # The transaction directory removal is the final cleanup commit
            # point.  The durable marker remains visible if this sync fails.
            os.fsync(directory_fd)
        except OSError as err:
            raise AtomicWritePostCommitError(
                "transaction cleanup fsync", err
            ) from err
        try:
            # Once the parent sync succeeds, the transaction removal is
            # durable.  Removing the now-unneeded marker is idempotent; if a
            # crash leaves it behind, it is harmless reconciliation evidence.
            remove_directory_at(directory_fd, recovery_name)
        except OSError as err:
            raise AtomicWritePostCommitError(
                "recovery marker cleanup", err
            ) from err
    except Exception:
        if file_fd is not None:
            try:
                os.close(file_fd)
            except OSError:
                pass
        if not committed:
            try:
                unlink_at(transaction_fd, temporary)
            except OSError:
                pass
            try:
                os.close(transaction_fd)
            except OSError:
                pass
            transaction_fd = None
            try:
                remove_directory_at(directory_fd, transaction_name)
            except OSError:
                pass
        raise
    finally:
        if transaction_fd is not None:
            try:
                os.close(transaction_fd)
            except OSError:
                pass


def list_names_checked(directory_fd):
    """List names through the held directory descriptor only.

    A pathname before/after check admits an ABA replacement: an attacker can
    swap in another directory for the enumeration and restore the original
    inode before the second check.  Supported runtimes must enumerate the held
    descriptor itself or fail closed.
    """
    directory_stat = os.fstat(directory_fd)
    if not stat.S_ISDIR(directory_stat.st_mode):
        raise NotADirectoryError(directory_fd)
    if _NATIVE_LISTDIR_FD:
        return os.listdir(directory_fd)

    duplicate_fd = os.dup(directory_fd)
    directory = _DIR_LIBC.fdopendir(duplicate_fd)
    if not directory:
        os.close(duplicate_fd)
        _raise_errno("fdopendir")
    names = []
    try:
        while True:
            ctypes.set_errno(0)
            entry = _READDIR(directory)
            if not entry:
                if ctypes.get_errno():
                    _raise_errno("readdir")
                break
            record = entry.contents
            record_address = ctypes.addressof(record)
            name_offset = _DIRENT.d_name.offset
            record_length = int(record.d_reclen)
            if not name_offset < record_length <= ctypes.sizeof(_DIRENT):
                raise ValueError("malformed directory entry record length")
            name_capacity = record_length - name_offset
            if sys.platform == "darwin":
                name_length = int(record.d_namlen)
                if (
                    record_length % 4
                    or not name_length
                    or name_length >= _DARWIN_D_NAME_SIZE
                    or name_length + 1 > name_capacity
                ):
                    raise ValueError("malformed Darwin directory entry name length")
                raw_record = ctypes.string_at(
                    record_address + name_offset, name_length + 1
                )
                if raw_record[-1:] != b"\0" or b"\0" in raw_record[:-1]:
                    raise ValueError("malformed Darwin directory entry name")
                padding = ctypes.string_at(
                    record_address + name_offset + name_length + 1,
                    record_length - name_offset - name_length - 1,
                )
                if any(padding):
                    raise ValueError("malformed Darwin directory entry padding")
                raw_name = raw_record[:-1]
            else:
                raw_record = ctypes.string_at(
                    record_address, min(record_length, ctypes.sizeof(_DIRENT))
                )
                raw_name = raw_record[name_offset:].split(b"\0", 1)[0]
                if not raw_name:
                    raise ValueError("malformed directory entry name")
            try:
                decoded_name = os.fsdecode(raw_name)
            except (UnicodeError, ValueError) as err:
                raise ValueError("malformed directory entry name") from err
            if raw_name in (b".", b".."):
                continue
            try:
                _component(decoded_name)
            except ValueError as err:
                raise ValueError("malformed directory entry name") from err
            names.append(decoded_name)
    finally:
        if _DIR_LIBC.closedir(directory) != 0:
            _raise_errno("closedir")
    return names
