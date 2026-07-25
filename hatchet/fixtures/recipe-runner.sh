#!/usr/bin/env bash
# OMP_RECIPE_RUNNER fixture: deterministic single-file git repository canary.
# Returns version-1 terminal JSON. Stages are driven by scenario files under
# hatchet/fixtures/scenarios so the workflow exercises every required path.
set -eu

recipe_path=""
task=""
cwd=""
stage=""
round=""
expected_head_sha=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --recipe) recipe_path="$2"; shift 2 ;;
    --task) task="$2"; shift 2 ;;
    --cwd) cwd="$2"; shift 2 ;;
    --stage) stage="$2"; shift 2 ;;
    --round) round="$2"; shift 2 ;;
    --head-sha) expected_head_sha="$2"; shift 2 ;;
    *) echo "fixture-runner: unknown argument: $1" >&2; exit 64 ;;
  esac
done

for required in recipe_path task cwd stage round expected_head_sha; do
  if [ -z "${!required:-}" ]; then
    echo "fixture-runner: missing --$required" >&2
    exit 64
  fi
done

scenario_file="${recipe_path%%::*}"
if [ ! -s "$scenario_file" ]; then
  echo "fixture-runner: scenario file not found: $scenario_file" >&2
  exit 64
fi

# shellcheck disable=SC1090
. "$scenario_file"

git rev-parse --git-dir >/dev/null 2>&1 || { echo "fixture-runner: cwd is not a git repo: $cwd" >&2; exit 64; }
actual_head=$(git -C "$cwd" rev-parse HEAD)
if [ "$actual_head" != "$expected_head_sha" ]; then
  echo "fixture-runner: head mismatch expected=$expected_head_sha actual=$actual_head" >&2
  exit 64
fi

scenario_name="${FIXTURE_SCENARIO:-happy}"
case "$stage" in
  implement)
    case "$scenario_name" in
      transient)
        marker="$cwd/.fixture-transient-failed"
        if [ ! -f "$marker" ]; then
          touch "$marker"
          echo "implement boom" >&2
          exit 70
        fi
        git -C "$cwd" commit --allow-empty -m "fixture implement $round" >/dev/null
        ;;
      stage-timeout)
        counter="$cwd/.fixture-attempt-count"
        count=$(( $(cat "$counter" 2>/dev/null || echo 0) + 1 ))
        echo "$count" > "$counter"
        echo "implement wedged" >&2
        exit 82
        ;;
      cancellation) echo "implement sleep" >&2; sleep 30 ;;
      *) git -C "$cwd" commit --allow-empty -m "fixture implement $round" >/dev/null ;;
    esac
    ;;
  adversarial_review)
    case "$scenario_name" in
      blocked-first|blocked-twice)
        echo '{"version":1,"outcome":"blocked","headSha":"'"$actual_head"'","artifactRefs":["review-blocked-'$round'"],"findings":"fixture review round '$round': blocking problem in fixture.ts:1"}'
        exit 0
        ;;
      *) echo '{"version":1,"outcome":"accepted","headSha":"'"$actual_head"'","artifactRefs":["review-accepted-'$round'"],"findings":"fixture review round '$round': checked everything, no blockers"}'
        exit 0 ;;
    esac
    ;;
  remediate)
    git -C "$cwd" commit --allow-empty -m "fixture remediate $round" >/dev/null
    ;;
  live_verify)
    case "$scenario_name" in
      verification-failed)
        echo '{"version":1,"outcome":"failed","headSha":"'"$actual_head"'","artifactRefs":["verify-failed"]}'
        exit 0
        ;;
      *) echo '{"version":1,"outcome":"verified","headSha":"'"$actual_head"'","artifactRefs":["verify-ok"]}'
        exit 0 ;;
    esac
    ;;
  terminal_evidence)
    ;;
  *) echo "fixture-runner: unknown stage: $stage" >&2; exit 64 ;;
esac

final_head=$(git -C "$cwd" rev-parse HEAD)
echo '{"version":1,"outcome":"completed","headSha":"'"$final_head"'","artifactRefs":["evidence-'$stage'-'$round'"]}'
