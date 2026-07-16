#!/usr/bin/env python3
"""Serve a descriptor-anchored local Artifact tree over static HTTP only."""

import argparse
import datetime
import email.utils
import os
import re
import stat
import urllib.parse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from artifact_fs import READ_FLAGS, normalized_absolute, open_at, open_child_directory, open_directory, open_regular_at


def request_parts(target):
    """Parse an origin-form request target into safe path components."""
    if re.search(r"%(?![0-9A-Fa-f]{2})", target):
        raise ValueError("malformed percent escape")
    parsed = urllib.parse.urlsplit(target)
    if parsed.scheme or parsed.netloc or parsed.fragment:
        raise ValueError("only origin-form local paths are accepted")
    decoded = urllib.parse.unquote(parsed.path, errors="strict")
    if not decoded.startswith("/") or any(ord(char) < 32 or ord(char) == 127 for char in decoded):
        raise ValueError("malformed request path")
    parts = [part for part in decoded.split("/") if part]
    if any(part in (".", "..") for part in parts):
        raise ValueError("relative path component")
    return parts, decoded.endswith("/"), parsed


class Handler(SimpleHTTPRequestHandler):
    """Static-only handler whose root is a held directory descriptor."""

    def _open_request(self, parts, trailing_slash):
        directory_fd = os.dup(self.server.root_fd)
        try:
            if trailing_slash:
                for component in parts:
                    child_fd = open_child_directory(directory_fd, component)
                    os.close(directory_fd)
                    directory_fd = child_fd
                return open_regular_at(directory_fd, "index.html"), False

            if not parts:
                return None, True
            for component in parts[:-1]:
                child_fd = open_child_directory(directory_fd, component)
                os.close(directory_fd)
                directory_fd = child_fd
            leaf_fd = open_at(directory_fd, parts[-1], READ_FLAGS)
            leaf_stat = os.fstat(leaf_fd)
            if stat.S_ISDIR(leaf_stat.st_mode):
                os.close(leaf_fd)
                return None, True
            if not stat.S_ISREG(leaf_stat.st_mode):
                os.close(leaf_fd)
                raise ValueError("request did not name a regular file")
            return leaf_fd, False
        finally:
            os.close(directory_fd)

    def send_head(self):
        try:
            parts, trailing_slash, parsed = request_parts(self.path)
            file_fd, redirect = self._open_request(parts, trailing_slash)
        except (OSError, UnicodeError, ValueError):
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        if redirect:
            canonical_path = "/" + "/".join(
                urllib.parse.quote(component, safe="") for component in parts
            ) + "/"
            location = urllib.parse.urlunsplit(("", "", canonical_path, parsed.query, ""))
            self.send_response(HTTPStatus.MOVED_PERMANENTLY)
            self.send_header("Location", location)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None

        file_object = os.fdopen(file_fd, "rb")
        try:
            file_stat = os.fstat(file_fd)
            if "If-Modified-Since" in self.headers and "If-None-Match" not in self.headers:
                try:
                    modified_since = email.utils.parsedate_to_datetime(
                        self.headers["If-Modified-Since"]
                    )
                except (TypeError, IndexError, OverflowError, ValueError):
                    pass
                else:
                    if modified_since.tzinfo is None:
                        modified_since = modified_since.replace(tzinfo=datetime.timezone.utc)
                    if modified_since.tzinfo is datetime.timezone.utc:
                        last_modified = datetime.datetime.fromtimestamp(
                            file_stat.st_mtime, datetime.timezone.utc
                        )
                        if last_modified.replace(microsecond=0) <= modified_since:
                            self.send_response(HTTPStatus.NOT_MODIFIED)
                            self.end_headers()
                            file_object.close()
                            return None

            served_name = parts[-1] if parts and not trailing_slash else "index.html"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", self.guess_type(served_name))
            self.send_header("Content-Length", str(file_stat.st_size))
            self.send_header("Last-Modified", self.date_time_string(file_stat.st_mtime))
            self.end_headers()
            return file_object
        except Exception:
            file_object.close()
            raise

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self' data:; script-src 'unsafe-inline'; "
            "style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'none'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
        )
        super().end_headers()

    def log_message(self, *args):
        pass


def port_number(value):
    port = int(value)
    if not 0 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 0 and 65535")
    return port


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        choices=("127.0.0.1", "localhost"),
        default="127.0.0.1",
        help="loopback address; external exposure belongs to a separate owner",
    )
    parser.add_argument("--port", type=port_number, default=8789)
    parser.add_argument("--root", default=os.path.expanduser("~/artifacts/public"))
    args = parser.parse_args()
    args.root = normalized_absolute(args.root)

    try:
        root_fd = open_directory(args.root, create=True)
    except (OSError, ValueError) as err:
        parser.error(str(err))

    server = None
    try:
        server = ThreadingHTTPServer((args.host, args.port), Handler)
        server.root_fd = root_fd
        bound_host, bound_port = server.server_address[:2]
        print(f"artifact_serve: {bound_host}:{bound_port} -> {args.root}", flush=True)
        server.serve_forever()
    finally:
        if server is not None:
            server.server_close()
        os.close(root_fd)


if __name__ == "__main__":
    main()
