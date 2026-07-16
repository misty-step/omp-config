#!/usr/bin/env python3
"""Descriptor-relative local filesystem boundary for ``sprite-lane``.

Caller-selected paths are traversed from held directory descriptors without
following symlinks. Local state is installed from anonymous descriptors with
typed commit outcomes. Snapshot brokers authenticate every request and response
without sending their secret over a reconnectable pathname socket.
"""

import base64
import ctypes
import errno
import hashlib
import hmac
import json
import os
import secrets
import shlex
import socket
import stat
import subprocess
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
    | getattr(os, "O_NONBLOCK", 0)
    | getattr(os, "O_CLOEXEC", 0)
)
CREATE_FLAGS = (
    os.O_WRONLY
    | os.O_CREAT
    | os.O_EXCL
    | getattr(os, "O_NOFOLLOW", 0)
    | getattr(os, "O_CLOEXEC", 0)
)
CREATE_RW_FLAGS = (CREATE_FLAGS & ~os.O_WRONLY) | os.O_RDWR
BROKER_LIMIT = 64 * 1024 * 1024
FRAME_LIMIT = 96 * 1024 * 1024

_LIBC = ctypes.CDLL(None, use_errno=True)
for _name in ("openat", "mkdirat", "unlinkat"):
    if not hasattr(_LIBC, _name):
        raise RuntimeError(f"local filesystem helper requires {_name}")


class DurabilityUnknown(OSError):
    """The namespace mutation committed but its directory fsync failed."""


class CommittedCleanupDebt(OSError):
    """The intended namespace mutation committed but recovery cleanup failed."""


def _call_int(function, *arguments):
    result = function(*arguments)
    if result < 0:
        value = ctypes.get_errno()
        raise OSError(value, os.strerror(value))
    return result


def open_at(directory_fd, name, flags, mode=0):
    return _call_int(
        _LIBC.openat,
        ctypes.c_int(directory_fd),
        ctypes.c_char_p(os.fsencode(name)),
        ctypes.c_int(flags),
        ctypes.c_int(mode),
    )


def mkdir_at(directory_fd, name, mode):
    _call_int(
        _LIBC.mkdirat,
        ctypes.c_int(directory_fd),
        ctypes.c_char_p(os.fsencode(name)),
        ctypes.c_uint(mode),
    )


def unlink_at(directory_fd, name):
    _call_int(
        _LIBC.unlinkat,
        ctypes.c_int(directory_fd),
        ctypes.c_char_p(os.fsencode(name)),
        ctypes.c_int(0),
    )


def normalized_absolute(path):
    value = os.path.abspath(os.path.expanduser(path))
    if sys.platform == "darwin":
        for alias, target in (("/tmp", "/private/tmp"), ("/var", "/private/var")):
            if value == alias or value.startswith(alias + os.path.sep):
                return target + value[len(alias) :]
    return value


def components(path):
    absolute = normalized_absolute(path)
    result = [part for part in absolute.split(os.path.sep) if part]
    if any(part in (".", "..") for part in result):
        raise ValueError("relative path components are not allowed")
    return result


def validate_leaf(leaf):
    if (
        not leaf
        or leaf in (".", "..")
        or os.path.sep in leaf
        or "\x00" in leaf
        or any(ord(character) < 32 for character in leaf)
    ):
        raise ValueError("leaf must be one plain filename")


def open_directory(path, create=False):
    directory_fd = os.open(os.path.sep, DIRECTORY_FLAGS)
    try:
        for component in components(path):
            try:
                child_fd = open_at(directory_fd, component, DIRECTORY_FLAGS)
            except OSError as err:
                if not create or err.errno != errno.ENOENT:
                    raise
                mkdir_at(directory_fd, component, 0o700)
                os.fsync(directory_fd)
                child_fd = open_at(directory_fd, component, DIRECTORY_FLAGS)
            os.close(directory_fd)
            directory_fd = child_fd
        if create:
            os.fchmod(directory_fd, 0o700)
        return directory_fd
    except Exception:
        os.close(directory_fd)
        raise


def split_parent(path):
    absolute = normalized_absolute(path)
    parent, leaf = os.path.split(absolute)
    validate_leaf(leaf)
    return parent, leaf


def open_regular(path, require_executable=False):
    parent, leaf = split_parent(path)
    directory_fd = open_directory(parent)
    try:
        source_fd = open_at(directory_fd, leaf, READ_FLAGS)
    finally:
        os.close(directory_fd)
    source_stat = os.fstat(source_fd)
    if not stat.S_ISREG(source_stat.st_mode):
        os.close(source_fd)
        raise ValueError("source is not a regular file")
    if require_executable and not source_stat.st_mode & 0o111:
        os.close(source_fd)
        raise ValueError("provider source is not executable")
    return source_fd


def anonymous_temp(directory_fd, prefix):
    if hasattr(os, "O_TMPFILE"):
        try:
            descriptor = os.open(
                ".",
                os.O_RDWR | os.O_TMPFILE | getattr(os, "O_CLOEXEC", 0),
                0o600,
                dir_fd=directory_fd,
            )
            os.fchmod(descriptor, 0o600)
            return descriptor
        except OSError as err:
            if err.errno not in (errno.EINVAL, errno.EISDIR, errno.EOPNOTSUPP):
                raise
    for _ in range(128):
        leaf = f".{prefix}.anonymous.{os.getpid()}.{os.urandom(12).hex()}"
        try:
            descriptor = open_at(directory_fd, leaf, CREATE_RW_FLAGS, 0o600)
            os.fchmod(descriptor, 0o600)
            unlink_at(directory_fd, leaf)
            return descriptor
        except OSError as err:
            if err.errno != errno.EEXIST:
                raise
    raise OSError(errno.EEXIST, "could not allocate an anonymous local-state inode")


def install_fd(source_fd, directory_fd, leaf):
    validate_leaf(leaf)
    if sys.platform == "darwin" and hasattr(_LIBC, "fclonefileat"):
        _call_int(
            _LIBC.fclonefileat,
            ctypes.c_int(source_fd),
            ctypes.c_int(directory_fd),
            ctypes.c_char_p(os.fsencode(leaf)),
            ctypes.c_uint(0),
        )
        return
    if hasattr(_LIBC, "linkat"):
        at_empty_path = 0x1000
        _call_int(
            _LIBC.linkat,
            ctypes.c_int(source_fd),
            ctypes.c_char_p(b""),
            ctypes.c_int(directory_fd),
            ctypes.c_char_p(os.fsencode(leaf)),
            ctypes.c_int(at_empty_path),
        )
        return
    raise OSError(errno.ENOTSUP, "descriptor install is unavailable")


def descriptor_install(directory, leaf, data):
    validate_leaf(leaf)
    if len(data) > 1024 * 1024:
        raise ValueError("local state exceeds the size limit")
    directory_fd = open_directory(directory, create=True)
    new_fd = None
    old_fd = None
    recovery_leaf = None
    try:
        try:
            old_fd = open_at(directory_fd, leaf, READ_FLAGS)
            if not stat.S_ISREG(os.fstat(old_fd).st_mode):
                raise ValueError("existing local state is not a regular file")
        except FileNotFoundError:
            old_fd = None
        new_fd = anonymous_temp(directory_fd, leaf)
        write_all(new_fd, data)
        os.fsync(new_fd)
        if old_fd is not None:
            for _ in range(128):
                candidate = f".{leaf}.recovery.{os.getpid()}.{os.urandom(12).hex()}"
                try:
                    install_fd(old_fd, directory_fd, candidate)
                    recovery_leaf = candidate
                    try:
                        os.fsync(directory_fd)
                    except OSError:
                        try:
                            unlink_at(directory_fd, recovery_leaf)
                            recovery_leaf = None
                        except OSError as cleanup_error:
                            recovery_path = os.path.join(normalized_absolute(directory), recovery_leaf)
                            raise OSError(
                                cleanup_error.errno,
                                f"recovery-link cleanup failed; retained recovery path {recovery_path}: {cleanup_error}",
                            ) from cleanup_error
                        raise
                    break
                except FileExistsError:
                    continue
            else:
                raise OSError(errno.EEXIST, "could not allocate local-state recovery link")
            unlink_at(directory_fd, leaf)
        try:
            install_fd(new_fd, directory_fd, leaf)
        except BaseException:
            if old_fd is not None:
                try:
                    install_fd(old_fd, directory_fd, leaf)
                    os.fsync(directory_fd)
                except OSError as restore_error:
                    recovery_path = os.path.join(normalized_absolute(directory), recovery_leaf)
                    raise OSError(
                        restore_error.errno,
                        f"local-state restore failed; retained recovery path {recovery_path}: {restore_error}",
                    ) from restore_error
            raise
        try:
            os.fsync(directory_fd)
        except OSError as err:
            detail = err.strerror
            if recovery_leaf is not None:
                recovery_path = os.path.join(normalized_absolute(directory), recovery_leaf)
                detail = f"{detail}; retained recovery path {recovery_path}"
            raise DurabilityUnknown(err.errno, detail) from err
        if recovery_leaf is not None:
            recovery_path = os.path.join(normalized_absolute(directory), recovery_leaf)
            try:
                unlink_at(directory_fd, recovery_leaf)
            except OSError as err:
                raise CommittedCleanupDebt(
                    err.errno,
                    f"committed local state; retained recovery path {recovery_path}: {err}",
                ) from err
            try:
                os.fsync(directory_fd)
            except OSError as err:
                raise CommittedCleanupDebt(
                    err.errno,
                    "committed local state; recovery-link removal durability is "
                    f"unknown and {recovery_path} may reappear after a crash: {err}",
                ) from err
            recovery_leaf = None
    finally:
        if new_fd is not None:
            os.close(new_fd)
        if old_fd is not None:
            os.close(old_fd)
        os.close(directory_fd)


def write_all(file_fd, data):
    view = memoryview(data)
    while view:
        written = os.write(file_fd, view)
        if written == 0:
            raise OSError(errno.EIO, "short write")
        view = view[written:]


def read_leaf(directory, leaf):
    validate_leaf(leaf)
    directory_fd = open_directory(directory)
    try:
        source_fd = open_at(directory_fd, leaf, READ_FLAGS)
    finally:
        os.close(directory_fd)
    try:
        metadata = os.fstat(source_fd)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("leaf is not a regular file")
        chunks = []
        total = 0
        while True:
            chunk = os.read(source_fd, 4096)
            if not chunk:
                return b"".join(chunks)
            total += len(chunk)
            if total > 1024 * 1024:
                raise ValueError("leaf exceeds the local state size limit")
            chunks.append(chunk)
    finally:
        os.close(source_fd)


def durable_remove(directory, leaf):
    validate_leaf(leaf)
    try:
        directory_fd = open_directory(directory)
    except FileNotFoundError:
        return
    removed = False
    try:
        try:
            unlink_at(directory_fd, leaf)
            removed = True
        except FileNotFoundError:
            return
        try:
            os.fsync(directory_fd)
        except OSError as err:
            raise DurabilityUnknown(err.errno, err.strerror) from err
    finally:
        os.close(directory_fd)
    if not removed:
        raise AssertionError("unreachable remove state")


def _send_frame(connection, value):
    payload = json.dumps(value, separators=(",", ":")).encode("utf-8")
    if len(payload) > FRAME_LIMIT:
        raise ValueError("broker response exceeds the size limit")
    connection.sendall(len(payload).to_bytes(8, "big") + payload)


def _receive_exact(connection, size):
    chunks = []
    remaining = size
    while remaining:
        chunk = connection.recv(remaining)
        if not chunk:
            raise EOFError("broker connection closed")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _receive_frame(connection):
    size = int.from_bytes(_receive_exact(connection, 8), "big")
    if size > FRAME_LIMIT:
        raise ValueError("broker request exceeds the size limit")
    return json.loads(_receive_exact(connection, size).decode("utf-8"))


def _parse_handle(handle):
    try:
        root, token = handle.rsplit("|", 1)
    except ValueError as err:
        raise ValueError("invalid snapshot recovery handle") from err
    if not root.startswith(os.path.sep) or len(token) != 64:
        raise ValueError("invalid snapshot recovery handle")
    try:
        bytes.fromhex(token)
    except ValueError as err:
        raise ValueError("invalid snapshot recovery handle") from err
    return normalized_absolute(root), token


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _authentication_code(key, direction, nonce, payload):
    message = direction.encode("ascii") + b"\0" + nonce.encode("ascii") + b"\0" + _canonical(payload)
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def _authenticated_request(key, envelope, seen_nonces):
    if not isinstance(envelope, dict):
        raise ValueError("invalid broker authentication envelope")
    nonce = envelope.get("nonce")
    request = envelope.get("request")
    supplied = envelope.get("mac")
    if not isinstance(nonce, str) or len(nonce) != 64:
        raise ValueError("invalid broker request nonce")
    try:
        bytes.fromhex(nonce)
    except ValueError as err:
        raise ValueError("invalid broker request nonce") from err
    if not isinstance(request, dict) or not isinstance(supplied, str):
        raise ValueError("invalid broker request envelope")
    expected = _authentication_code(key, "request", nonce, request)
    if not hmac.compare_digest(supplied, expected):
        raise PermissionError("snapshot authentication failed")
    if nonce in seen_nonces:
        raise PermissionError("replayed snapshot request")
    if len(seen_nonces) >= 4096:
        raise OSError(errno.ENOSPC, "snapshot replay window is full")
    seen_nonces.add(nonce)
    return nonce, request


def _send_authenticated(connection, key, nonce, response):
    _send_frame(
        connection,
        {
            "nonce": nonce,
            "response": response,
            "mac": _authentication_code(key, "response", nonce, response),
        },
    )


def _held_bytes(snapshot_fd, limit=BROKER_LIMIT):
    os.lseek(snapshot_fd, 0, os.SEEK_SET)
    chunks = []
    total = 0
    while True:
        chunk = os.read(snapshot_fd, 64 * 1024)
        if not chunk:
            return b"".join(chunks)
        total += len(chunk)
        if total > limit:
            raise ValueError("snapshot exceeds the broker size limit")
        chunks.append(chunk)


def _broker_call(handle, request):
    root, token = _parse_handle(handle)
    key = bytes.fromhex(token)
    nonce = secrets.token_hex(32)
    envelope = {
        "nonce": nonce,
        "request": request,
        "mac": _authentication_code(key, "request", nonce, request),
    }
    connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        connection.connect(os.path.join(root, "broker.sock"))
        _send_frame(connection, envelope)
        reply = _receive_frame(connection)
    finally:
        connection.close()
    if not isinstance(reply, dict) or reply.get("nonce") != nonce:
        raise PermissionError("snapshot response authentication failed")
    response = reply.get("response")
    supplied = reply.get("mac")
    if not isinstance(response, dict) or not isinstance(supplied, str):
        raise PermissionError("snapshot response authentication failed")
    expected = _authentication_code(key, "response", nonce, response)
    if not hmac.compare_digest(supplied, expected):
        raise PermissionError("snapshot response authentication failed")
    return response


def _broker_execute(root, root_fd, snapshot_fd, arguments, environment, input_data):
    executable_fd = None
    executable_leaf = None
    primary = 1
    stdout = b""
    stderr = b""
    cleanup_debt = None
    try:
        header = os.pread(snapshot_fd, 4096, 0)
        pass_descriptors = (snapshot_fd,)
        if header.startswith(b"#!"):
            first_line = header.split(b"\n", 1)[0][2:].decode("utf-8")
            interpreter = shlex.split(first_line)
            if not interpreter or not interpreter[0].startswith("/"):
                raise OSError(errno.ENOEXEC, "invalid provider shebang")
            command = [*interpreter, f"/dev/fd/{snapshot_fd}", *arguments]
        elif sys.platform != "darwin" and os.path.isdir("/proc/self/fd"):
            command = [f"/proc/self/fd/{snapshot_fd}", *arguments]
        elif sys.platform == "darwin" and hasattr(_LIBC, "fclonefileat"):
            # Darwin exposes no fexecve/execveat and mounts /dev/fd non-executable.
            # Derive one unpredictable, private execution leaf from the held
            # snapshot, open it before launch, and unlink it as soon as spawn
            # resolves the binary. Scripts and Linux binaries never use this
            # pathname compatibility boundary.
            executable_leaf = f".provider-exec.{os.getpid()}.{secrets.token_hex(16)}"
            install_fd(snapshot_fd, root_fd, executable_leaf)
            executable_fd = open_at(root_fd, executable_leaf, READ_FLAGS)
            command = [os.path.join(root, executable_leaf), *arguments]
            pass_descriptors = ()
        else:
            raise OSError(errno.ENOTSUP, "descriptor-authoritative provider execution is unavailable")
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
            pass_fds=pass_descriptors,
        )
        process_stdout, process_stderr = process.communicate(input_data)
        primary = process.returncode if process.returncode >= 0 else 128 - process.returncode
        stdout = process_stdout
        stderr += process_stderr
        if executable_leaf is not None:
            try:
                _unlink_held(root_fd, executable_leaf, executable_fd)
                os.fsync(root_fd)
                executable_leaf = None
            except OSError as err:
                cleanup_debt = os.path.join(root, executable_leaf)
                stderr += (
                    f"stage_card.py: provider execution cleanup debt retained at "
                    f"{cleanup_debt}: {err}\n"
                ).encode()
        if cleanup_debt is not None and primary == 0:
            primary = 1
    except OSError as err:
        stderr = f"stage_card.py: provider broker execution failed: {err}\n".encode()
    finally:
        if executable_leaf is not None and executable_fd is not None:
            try:
                _unlink_held(root_fd, executable_leaf, executable_fd)
                os.fsync(root_fd)
            except OSError as err:
                cleanup_debt = os.path.join(root, executable_leaf)
                stderr += (
                    f"stage_card.py: provider execution cleanup debt retained at "
                    f"{cleanup_debt}: {err}\n"
                ).encode()
                if primary == 0:
                    primary = 1
        elif executable_leaf is not None:
            try:
                os.stat(executable_leaf, dir_fd=root_fd, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                cleanup_debt = os.path.join(root, executable_leaf)
                stderr += (
                    f"stage_card.py: provider execution cleanup state is unknown; "
                    f"inspect recovery path {cleanup_debt}\n"
                ).encode()
                if primary == 0:
                    primary = 1
        if executable_fd is not None:
            os.close(executable_fd)
    return {
        "ok": True,
        "status": primary,
        "stdout": base64.b64encode(stdout).decode("ascii"),
        "stderr": base64.b64encode(stderr).decode("ascii"),
        "cleanup_debt": cleanup_debt,
    }


def _unlink_held(directory_fd, leaf, held_fd):
    try:
        current = os.stat(leaf, dir_fd=directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    held = os.fstat(held_fd)
    if (current.st_dev, current.st_ino) != (held.st_dev, held.st_ino):
        raise OSError(errno.ESTALE, f"refusing to remove replacement snapshot leaf {leaf}")
    unlink_at(directory_fd, leaf)


def _serve_broker(root, root_fd, snapshot_fd, listener, token, kind):
    key = bytes.fromhex(token)
    seen_nonces = set()
    terminate = False
    while not terminate:
        connection, _ = listener.accept()
        nonce = None
        try:
            nonce, request = _authenticated_request(
                key, _receive_frame(connection), seen_nonces
            )
            operation = request.get("operation")
            if operation == "read" and kind == "card":
                response = {
                    "ok": True,
                    "data": base64.b64encode(
                        _held_bytes(snapshot_fd, 1024 * 1024)
                    ).decode("ascii"),
                }
            elif operation == "execute" and kind == "provider":
                arguments = request.get("arguments")
                environment = request.get("environment")
                if not isinstance(arguments, list) or not all(
                    isinstance(item, str) for item in arguments
                ):
                    raise ValueError("invalid provider arguments")
                if not isinstance(environment, dict) or not all(
                    isinstance(key, str) and isinstance(value, str)
                    for key, value in environment.items()
                ):
                    raise ValueError("invalid provider environment")
                input_data = base64.b64decode(request.get("input", ""), validate=True)
                response = _broker_execute(
                    root,
                    root_fd,
                    snapshot_fd,
                    arguments,
                    environment,
                    input_data,
                )
            elif operation == "discard":
                socket_removed = False
                try:
                    _unlink_held(root_fd, "snapshot", snapshot_fd)
                    os.fsync(root_fd)
                    unlink_at(root_fd, "broker.sock")
                    socket_removed = True
                    os.fsync(root_fd)
                    os.rmdir(root)
                    response = {"ok": True}
                    terminate = True
                except OSError as err:
                    response = {"ok": False, "error": str(err), "recovery": root}
                    if socket_removed:
                        terminate = True
            else:
                response = {"ok": False, "error": "invalid broker operation"}
            _send_authenticated(connection, key, nonce, response)
        except (EOFError, OSError, ValueError, json.JSONDecodeError) as err:
            if nonce is not None:
                try:
                    _send_authenticated(
                        connection,
                        key,
                        nonce,
                        {"ok": False, "error": str(err), "recovery": root},
                    )
                except OSError:
                    pass
        finally:
            connection.close()
    listener.close()
    os.close(snapshot_fd)
    os.close(root_fd)


def start_broker(path, kind):
    if kind not in ("card", "provider"):
        raise ValueError("invalid broker kind")
    source_fd = open_regular(path, require_executable=kind == "provider")
    # Unix-domain socket paths are short on macOS; the literal system temp root
    # also avoids caller-selected parents becoming broker authority.
    temporary_root = normalized_absolute("/tmp")
    temporary_root_fd = open_directory(temporary_root)
    root = None
    root_fd = None
    snapshot_fd = None
    listener = None
    token = secrets.token_hex(32)
    try:
        for _ in range(128):
            root_leaf = f"roster-sprite-broker-{os.getpid()}-{secrets.token_hex(12)}"
            try:
                mkdir_at(temporary_root_fd, root_leaf, 0o700)
                os.fsync(temporary_root_fd)
                break
            except OSError as err:
                if err.errno != errno.EEXIST:
                    raise
        else:
            raise OSError(errno.EEXIST, "could not allocate snapshot broker directory")
        root = os.path.join(temporary_root, root_leaf)
        root_fd = open_at(temporary_root_fd, root_leaf, DIRECTORY_FLAGS)
        snapshot_fd = open_at(root_fd, "snapshot", CREATE_RW_FLAGS, 0o500 if kind == "provider" else 0o400)
        os.fchmod(snapshot_fd, 0o500 if kind == "provider" else 0o400)
        with os.fdopen(source_fd, "rb", closefd=True) as source:
            source_fd = None
            while True:
                chunk = source.read(64 * 1024)
                if not chunk:
                    break
                write_all(snapshot_fd, chunk)
                if os.lseek(snapshot_fd, 0, os.SEEK_CUR) > BROKER_LIMIT:
                    raise ValueError("snapshot exceeds the broker size limit")
        os.fsync(snapshot_fd)
        os.fsync(root_fd)
        read_snapshot_fd = open_at(root_fd, "snapshot", READ_FLAGS)
        read_snapshot = os.fstat(read_snapshot_fd)
        written_snapshot = os.fstat(snapshot_fd)
        if (read_snapshot.st_dev, read_snapshot.st_ino) != (
            written_snapshot.st_dev,
            written_snapshot.st_ino,
        ):
            os.close(read_snapshot_fd)
            raise OSError(errno.ESTALE, "snapshot pathname changed during creation")
        os.close(snapshot_fd)
        snapshot_fd = read_snapshot_fd
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(os.path.join(root, "broker.sock"))
        os.chmod(os.path.join(root, "broker.sock"), 0o600)
        listener.listen(4)
        process = os.fork()
        if process:
            listener.close()
            os.close(snapshot_fd)
            os.close(root_fd)
            return f"{root}|{token}"
        os.setsid()
        null_fd = os.open(os.devnull, os.O_RDWR)
        for descriptor in (0, 1, 2):
            os.dup2(null_fd, descriptor)
        if null_fd > 2:
            os.close(null_fd)
        os.close(temporary_root_fd)
        _serve_broker(root, root_fd, snapshot_fd, listener, token, kind)
        os._exit(0)
    except BaseException:
        if listener is not None:
            listener.close()
        if snapshot_fd is not None:
            os.close(snapshot_fd)
        if root_fd is not None:
            try:
                unlink_at(root_fd, "snapshot")
            except OSError:
                pass
            os.close(root_fd)
        if root is not None:
            try:
                os.rmdir(root)
            except OSError:
                pass
        raise
    finally:
        if source_fd is not None:
            os.close(source_fd)
        os.close(temporary_root_fd)


def broker_read(handle):
    response = _broker_call(handle, {"operation": "read"})
    if not response.get("ok"):
        raise OSError(response.get("error", "snapshot read failed"))
    return base64.b64decode(response["data"], validate=True)


def broker_execute(handle, input_handle, arguments):
    input_data = broker_read(input_handle) if input_handle else b""
    environment = {
        "HOME": os.environ["HOME"],
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "LANG": os.environ.get("LANG", "C"),
        "XDG_CONFIG_HOME": os.environ.get("XDG_CONFIG_HOME", os.path.join(os.environ["HOME"], ".config")),
    }
    response = _broker_call(
        handle,
        {
            "operation": "execute",
            "arguments": arguments,
            "environment": environment,
            "input": base64.b64encode(input_data).decode("ascii"),
        },
    )
    if not response.get("ok"):
        raise OSError(response.get("error", "provider execution failed"))
    sys.stdout.buffer.write(base64.b64decode(response["stdout"], validate=True))
    sys.stderr.buffer.write(base64.b64decode(response["stderr"], validate=True))
    return int(response["status"])


def broker_discard(handle):
    root, _ = _parse_handle(handle)
    response = _broker_call(handle, {"operation": "discard"})
    if not response.get("ok"):
        recovery = response.get("recovery", root)
        raise OSError(f"snapshot cleanup failed; retained recovery path {recovery}: {response.get('error', 'unknown error')}")


def main():
    if len(sys.argv) < 2:
        raise SystemExit(
            "usage: stage_card.py "
            "<broker-start|broker-exec|broker-discard|read|install|remove> ..."
        )
    command = sys.argv[1]
    try:
        if command == "broker-start" and len(sys.argv) == 4:
            print(start_broker(sys.argv[3], sys.argv[2]))
        elif command == "broker-exec" and len(sys.argv) >= 5:
            input_handle = None if sys.argv[3] == "-" else sys.argv[3]
            if sys.argv[4] != "--":
                raise ValueError("broker-exec requires -- before provider arguments")
            raise SystemExit(broker_execute(sys.argv[2], input_handle, sys.argv[5:]))
        elif command == "broker-discard" and len(sys.argv) == 3:
            broker_discard(sys.argv[2])
        elif command == "read" and len(sys.argv) == 4:
            sys.stdout.buffer.write(read_leaf(sys.argv[2], sys.argv[3]))
        elif command == "install" and len(sys.argv) == 4:
            descriptor_install(sys.argv[2], sys.argv[3], sys.stdin.buffer.read(1024 * 1024 + 1))
        elif command == "remove" and len(sys.argv) == 4:
            durable_remove(sys.argv[2], sys.argv[3])
        else:
            raise ValueError("invalid command or argument count")
    except DurabilityUnknown as err:
        print(f"stage_card.py: durability-unknown after namespace commit: {err}", file=sys.stderr)
        raise SystemExit(20) from err
    except CommittedCleanupDebt as err:
        print(f"stage_card.py: committed with cleanup debt: {err}", file=sys.stderr)
        raise SystemExit(21) from err
    except (OSError, ValueError) as err:
        raise SystemExit(f"stage_card.py: {err}") from err


if __name__ == "__main__":
    main()
