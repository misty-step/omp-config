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
	updated="$(date -u +%s 2>/dev/null || date +%s)"
	source="builtin"
	payload=""

	script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
	analyze_ts="$script_dir/analyze.ts"
	if [ ! -f "$analyze_ts" ] && [ -f "$ROOT/extensions/loc/analyze.ts" ]; then
		analyze_ts="$ROOT/extensions/loc/analyze.ts"
	fi

	if command -v scc >/dev/null 2>&1; then
		if scc -f json --exclude-dir node_modules --exclude-dir .git >"$TMP.scc" 2>/dev/null; then
			if command -v bun >/dev/null 2>&1; then
				payload="$(bun -e '
const fs = require("node:fs");
const rows = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
const out = {};
let files = 0, total = 0, code = 0, comment = 0, blank = 0;
for (const row of rows) {
  if (!row?.Name || row.Name === "Total") continue;
  const f = Number(row.Count || 0);
  const b = Number(row.Blanks || 0);
  const c = Number(row.Code || 0);
  const m = Number(row.Comment || 0);
  out[row.Name] = { files: f, total: c + m + b, code: c, comment: m, blank: b };
  files += f; blank += b; code += c; comment += m; total += c + m + b;
}
process.stdout.write(JSON.stringify({ files, total, code, comment, blank, byLanguage: out, source: "scc" }));
' "$TMP.scc")"
				source="scc"
			fi
		fi
	elif command -v tokei >/dev/null 2>&1; then
		if tokei -o json >"$TMP.tokei" 2>/dev/null; then
			if command -v bun >/dev/null 2>&1; then
				payload="$(bun -e '
const fs = require("node:fs");
const parsed = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
const out = {};
let files = 0, total = 0, code = 0, comment = 0, blank = 0;
for (const [language, reports] of Object.entries(parsed)) {
  if (language === "Total") continue;
  let lf = 0, lb = 0, lc = 0, lm = 0;
  for (const report of Object.values(reports)) {
    lf += 1;
    lb += Number(report.blanks || 0);
    lc += Number(report.code || 0);
    lm += Number(report.comments || 0);
  }
  if (!lf) continue;
  out[language] = { files: lf, total: lc + lm + lb, code: lc, comment: lm, blank: lb };
  files += lf; blank += lb; code += lc; comment += lm; total += lc + lm + lb;
}
process.stdout.write(JSON.stringify({ files, total, code, comment, blank, byLanguage: out, source: "tokei" }));
' "$TMP.tokei")"
				source="tokei"
			fi
		fi
	fi

	if [ -z "$payload" ] && command -v bun >/dev/null 2>&1 && [ -f "$analyze_ts" ]; then
		payload="$(cd "$ROOT" && bun "$analyze_ts" --json 2>/dev/null || true)"
		source="builtin"
	fi

	if [ -z "$payload" ]; then
		payload='{"files":0,"total":0,"code":0,"comment":0,"blank":0,"byLanguage":{},"source":"builtin"}'
	fi

	case "$payload" in
		*\"updatedAt\":*) printf '%s\n' "$payload" >"$TMP" ;;
		*) printf '%s\n' "$payload" | sed "s/}$/,\"updatedAt\":$updated}/" >"$TMP" ;;
	esac
	mv -f "$TMP" "$CACHE"
	rm -f "$TMP.scc" "$TMP.tokei" 2>/dev/null || true

	if command -v jq >/dev/null 2>&1; then
		code="$(jq -r '.code // 0' "$CACHE")"
		files="$(jq -r '.files // 0' "$CACHE")"
		total="$(jq -r '.total // 0' "$CACHE")"
		source="$(jq -r '.source // "builtin"' "$CACHE")"
	elif command -v bun >/dev/null 2>&1; then
		eval "$(bun -e '
const fs = require("node:fs");
const data = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
process.stdout.write(`code=${data.code ?? 0}\nfiles=${data.files ?? 0}\ntotal=${data.total ?? 0}\nsource=${data.source ?? "builtin"}`);
' "$CACHE")"
	else
		code=0
		files=0
		total=0
	fi
	printf 'LOC_CODE=%s LOC_FILES=%s LOC_TOTAL=%s LOC_SOURCE=%s\n' "${code:-0}" "${files:-0}" "${total:-0}" "${source:-builtin}" >"$ROOT/.git/loc_cache.env"
}

write_cache
