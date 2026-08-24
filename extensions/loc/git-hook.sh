#!/bin/sh
# POSIX git hook: refresh .git/loc_cache asynchronously for instant statusline reads.
# Install: ln -sf ../../extensions/loc/git-hook.sh .git/hooks/post-commit
#          ln -sf ../../extensions/loc/git-hook.sh .git/hooks/post-merge
#          ln -sf ../../extensions/loc/git-hook.sh .git/hooks/post-checkout

set -eu

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
CACHE="$ROOT/.git/loc_cache"
TMP="$ROOT/.git/loc_cache.tmp.$$"
LOCK="$ROOT/.git/loc_cache.lock"
LOG="$ROOT/.git/loc_cache.log"

if [ "${LOC_CACHE_BACKGROUND:-}" != "1" ]; then
	LOC_CACHE_BACKGROUND=1
	export LOC_CACHE_BACKGROUND
	(
		exec "$0" "$@"
	) >>"$LOG" 2>&1 &
	exit 0
fi

if ! mkdir "$LOCK" 2>/dev/null; then
	exit 0
fi

cleanup() {
	rmdir "$LOCK" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

write_cache() {
	script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
	analyze_ts="$script_dir/analyze.ts"
	if [ ! -f "$analyze_ts" ] && [ -f "$ROOT/extensions/loc/analyze.ts" ]; then
		analyze_ts="$ROOT/extensions/loc/analyze.ts"
	fi
	if ! command -v bun >/dev/null 2>&1 || [ ! -f "$analyze_ts" ]; then
		return 0
	fi

	payload="$(cd "$ROOT" && bun "$analyze_ts" --json --cwd "$ROOT")"
	printf '%s\n' "$payload" >"$TMP"
	mv -f "$TMP" "$CACHE"

	code=0
	files=0
	total=0
	source=builtin
	if command -v jq >/dev/null 2>&1; then
		code="$(jq -r '.code // 0' "$CACHE")"
		files="$(jq -r '.files // 0' "$CACHE")"
		total="$(jq -r '.total // 0' "$CACHE")"
		source="$(jq -r '.source // "builtin"' "$CACHE")"
	else
		eval "$(bun -e '
const fs = require("node:fs");
const data = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
process.stdout.write(`code=${data.code ?? 0}\nfiles=${data.files ?? 0}\ntotal=${data.total ?? 0}\nsource=${data.source ?? "builtin"}`);
' "$CACHE")"
	fi
	printf 'LOC_CODE=%s LOC_FILES=%s LOC_TOTAL=%s LOC_SOURCE=%s\n' "$code" "$files" "$total" "$source" >"$ROOT/.git/loc_cache.env"
}

write_cache
