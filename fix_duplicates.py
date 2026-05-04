import os
import re
from pathlib import Path

def fix_duplicates():
    repo_root = Path('.').absolute()
    artifacts = list(repo_root.glob('docs/**/*/*.md'))
    id_map = {}
    
    # Pattern to find ID in filename or content (simplistic for now)
    # We'll use the error message's specific duplicates
    duplicates = {
        "EPIC-064": [
            "docs/epic/Active/(EPIC-064)-Title-Based-Artifact-Migration/(EPIC-064)-Title-Based-Artifact-Migration.md",
            "docs/epic/Proposed/(EPIC-064)-Appraisal-Value-Model/(EPIC-064)-Appraisal-Value-Model.md"
        ],
        "SPEC-257": [
            "docs/spec/Active/(SPEC-257)-Swain-Do-Completion-Chain/(SPEC-257)-Swain-Do-Completion-Chain.md",
            "docs/spec/Active/SPEC-257-consolidate-swain-init-preflight.md"
        ],
        "SPEC-259": [
            "docs/spec/Active/(SPEC-259)-Consumer-Gitignore-Coverage-Gaps/(SPEC-259)-Consumer-Gitignore-Coverage-Gaps.md",
            "docs/spec/Active/(SPEC-259)-Swain-Sync-Preflight-Script.md"
        ],
        "SPEC-293": [
            "docs/spec/Active/(SPEC-293)-CLI-Tool-Research-Pattern-For-Swain-Search/SPEC-293.md",
            "docs/spec/Active/(SPEC-293)-Output-Shaping-For-Chat/(SPEC-293)-Output-Shaping-For-Chat.md"
        ],
        "SPIKE-052": [
            "docs/research/Proposed/(SPIKE-052)-Reporting-Format-Library-Design/(SPIKE-052)-Reporting-Format-Library-Design.md",
            "docs/spike/Active/(SPIKE-052)-Session-Startup-Time-Instrumentation/(SPIKE-052)-Session-Startup-Time-Instrumentation.md"
        ],
        "SPIKE-058": [
            "docs/research/Active/(SPIKE-058)-Embedding-Nearest-Neighbor-Artifact-Navigation/(SPIKE-058)-Embedding-Nearest-Neighbor-Artifact-Navigation.md",
            "docs/spike/Proposed/(SPIKE-058)-Agent-Runtime-IO-Compatibility-For-Mobile-Bridge/(SPIKE-058)-Agent-Runtime-IO-Compatibility-For-Mobile-Bridge.md"
        ],
        "SPIKE-059": [
            "docs/research/Complete/(SPIKE-059)-ROI-Appraisal-Model-For-Portfolio-Economics/SPIKE-059.md",
            "docs/spike/Complete/(SPIKE-059)-Agent-Runtime-IO-Compatibility-For-Mobile-Bridge/(SPIKE-059)-Agent-Runtime-IO-Compatibility-For-Mobile-Bridge.md"
        ],
        "SPIKE-060": [
            "docs/research/Proposed/(SPIKE-060)-Cost-Axis-Composition-Model/SPIKE-060.md",
            "docs/spike/Complete/(SPIKE-060)-Ollama-Launch-Argument-Passthrough/(SPIKE-060)-Ollama-Launch-Argument-Passthrough.md"
        ],
        "SPIKE-061": [
            "docs/research/Active/(SPIKE-061)-Doctor-Script-Simplification/(SPIKE-061)-Doctor-Script-Simplification.md",
            "docs/spike/Active/(SPIKE-061)-Swain-Runtime-Adapter-Architecture/(SPIKE-061)-Swain-Runtime-Adapter-Architecture.md"
        ],
        "SPIKE-062": [
            "docs/research/Active/(SPIKE-062)-Doctor-Python-Migration/(SPIKE-062)-Doctor-Python-Migration.md",
            "docs/spike/Active/(SPIKE-062)-Session-Recovery-After-Host-Restart/(SPIKE-062)-Session-Recovery-After-Host-Restart.md"
        ]
    }

    for art_id, paths in duplicates.items():
        # We will keep the first one and rename the second one to a new ID
        # But simpler: since I can't easily guess "next ID" safely here without a script,
        # I'll just notify the user or try to find a safe increment.
        # Actually, the user asked to "fix error", I should probably just use next-artifact-id.sh.
        pass

if __name__ == "__main__":
    fix_duplicates()
