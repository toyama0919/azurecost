#!/usr/bin/env bash
#
# Cut a PyPI release for azurecost.
#
# Bump pyproject.toml's version -> commit to main -> push a matching
# v<version> tag, which triggers the "release" GitHub Actions workflow
# (Trusted Publisher / OIDC, no token). The tag is always derived from
# pyproject.toml so the two never drift.
#
# Usage:
#   release.sh [patch|minor|major|X.Y.Z]
#   (no argument defaults to "patch")
#
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

BUMP="${1:-patch}"

die() { echo "release: $*" >&2; exit 1; }

# --- Step 0: guard the working state ----------------------------------------
[[ "$(git branch --show-current)" == "main" ]] || die "not on main"
[[ -z "$(git status --porcelain)" ]] || die "working tree is not clean"
git fetch origin
[[ "$(git rev-parse @)" == "$(git rev-parse '@{u}')" ]] || die "local main is not up to date with origin"

# --- Step 1: read the current version ---------------------------------------
CUR="$(grep -E '^version = "' pyproject.toml | head -1 | sed -E 's/^version = "([^"]+)".*/\1/')"
[[ "$CUR" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "unexpected version in pyproject.toml: '$CUR' (expected X.Y.Z)"

# --- Step 2: compute the new version ----------------------------------------
if [[ "$BUMP" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  NEW="$BUMP"
else
  IFS='.' read -r MAJ MIN PAT <<<"$CUR"
  case "$BUMP" in
    major) NEW="$((MAJ + 1)).0.0" ;;
    minor) NEW="${MAJ}.$((MIN + 1)).0" ;;
    patch) NEW="${MAJ}.${MIN}.$((PAT + 1))" ;;
    *) die "unknown bump '$BUMP' (expected patch|minor|major|X.Y.Z)" ;;
  esac
fi
echo "release: $CUR -> $NEW"

# --- Step 3: guard against collisions ---------------------------------------
[[ -z "$(git tag -l "v$NEW")" ]] || die "tag v$NEW already exists locally"
[[ -z "$(git ls-remote --tags origin "v$NEW")" ]] || die "tag v$NEW already exists on origin"
CODE="$(curl -s -o /dev/null -w '%{http_code}' "https://pypi.org/pypi/azurecost/$NEW/json" || echo 000)"
[[ "$CODE" != "200" ]] || die "azurecost $NEW is already on PyPI"

# --- Step 4: edit pyproject.toml --------------------------------------------
# Only the leading `version = "..."` (the project version), not deps.
perl -i -pe 'BEGIN{$n=0} if(!$n && /^version = "/){s/^version = "[^"]+"/version = "'"$NEW"'"/; $n=1}' pyproject.toml

# --- Step 5: sanity gate (mirror scripts/ci.sh run-test) --------------------
if ! tox -e black || ! tox -e flake8 || ! tox -e pytest; then
  git checkout pyproject.toml
  die "sanity gate failed; reverted pyproject.toml"
fi

# --- Step 6: commit to main, tag locally, then push both --------------------
# Tag locally BEFORE pushing so that if the tag push fails after main is
# pushed, the tag already exists and recovery is a single re-push.
# When pyproject.toml already carries $NEW (version bumped in an earlier
# commit), there is nothing to commit -- tag HEAD as-is.
git add pyproject.toml
if git diff --cached --quiet; then
  echo "release: pyproject.toml already at $NEW; tagging HEAD without a new commit"
else
  git commit -m "Release v$NEW"
fi
git tag "v$NEW"
git push origin main

# --- Step 7: push the tag (this triggers the publish workflow) --------------
if ! git push origin "v$NEW"; then
  die "main is pushed but tag push failed. Recover with: git push origin v$NEW"
fi

# --- Step 8: confirm the publish --------------------------------------------
# The release is already committed and tagged; this only waits for the async
# publish workflow. A timeout here means "not confirmed yet", NOT "failed".
echo "release: tag pushed; waiting for PyPI to publish v$NEW ..."
for _ in $(seq 1 30); do
  CODE="$(curl -s -o /dev/null -w '%{http_code}' "https://pypi.org/pypi/azurecost/$NEW/json" || echo 000)"
  if [[ "$CODE" == "200" ]]; then
    echo "release: published https://pypi.org/project/azurecost/$NEW/"
    exit 0
  fi
  sleep 10
done
echo "release: v$NEW not on PyPI yet (publish may still be running) — check the Actions tab" >&2
exit 2
