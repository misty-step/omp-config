#!/bin/sh
set -eu
# Fail if this generated copy differs from the Exocortex repository source.
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DEST="$HERE/SKILL.md"
SRC=${EXOCORTEX_SKILL_SOURCE:-}
if [ -z "$SRC" ]; then
	guess="$HERE/../../../exocortex/skills/exocortex/SKILL.md"
	if [ -f "$guess" ]; then
		SRC=$guess
	else
		printf 'set EXOCORTEX_SKILL_SOURCE to misty-step/exocortex skills/exocortex/SKILL.md\n' >&2
		exit 2
	fi
fi
cmp "$SRC" "$DEST"
printf 'exocortex skill matches source %s\n' "$SRC"
