#!/usr/bin/env bash
# legacy-skills-lib.sh — shared helpers for stale swain skill detection

legacy_skills_json_path() {
  echo "$SKILL_DIR/references/legacy-skills.json"
}

legacy_skill_entries() {
  local json_path="${1:-$(legacy_skills_json_path)}"
  python3 - "$json_path" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    data = json.load(handle)

for kind in ("renamed", "retired"):
    for old_name, replacement in data.get(kind, {}).items():
        print(f"{kind}\t{old_name}\t{replacement}")
PY
}

legacy_skill_fingerprints() {
  local json_path="${1:-$(legacy_skills_json_path)}"
  python3 - "$json_path" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    data = json.load(handle)

for fingerprint in data.get("fingerprints", []):
    print(fingerprint)
PY
}

legacy_skill_matches_fingerprint() {
  local skill_dir="$1"
  local json_path="${2:-$(legacy_skills_json_path)}"
  local skill_file="$skill_dir/SKILL.md"

  [[ -f "$skill_file" ]] || return 1

  while IFS= read -r fingerprint; do
    [[ -n "$fingerprint" ]] || continue
    if grep -F -q -- "$fingerprint" "$skill_file"; then
      return 0
    fi
  done < <(legacy_skill_fingerprints "$json_path")

  return 1
}
