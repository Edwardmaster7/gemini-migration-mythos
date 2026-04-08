#!/usr/bin/env python3
"""
diff_versions.py — Multi-version legacy repository comparator.

Compares N versions of the same legacy system (organized as subdirectories)
and produces a behavioral diff for a given feature across versions.

Usage:
    python diff_versions.py --root <LEGACY_ROOT> --feature "<FEATURE_NAME>"
    python diff_versions.py --root <LEGACY_ROOT> --feature "<FEATURE_NAME>" --output version_diff.json
"""

import argparse
import difflib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
CODE_EXTENSIONS = {".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".cs", ".rs"}
VERSION_PATTERNS = ["v", "version", "release", "ver"]


def discover_versions(root: Path) -> list[dict]:
    """Discover version directories under the root path."""
    versions = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if entry.name in IGNORE_DIRS:
            continue
        is_versioned = any(
            entry.name.lower().startswith(p) for p in VERSION_PATTERNS
        ) or entry.name[0].isdigit()
        versions.append({
            "name": entry.name,
            "path": entry,
            "is_versioned": is_versioned,
        })
    return versions


def find_feature_files(version_path: Path, feature_terms: list[str]) -> list[str]:
    """Find files related to a feature in a version directory."""
    matches = []
    for root, dirs, files in os.walk(version_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for fname in files:
            fpath = Path(root) / fname
            if fpath.suffix.lower() not in CODE_EXTENSIONS:
                continue
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                if any(term.lower() in content.lower() for term in feature_terms):
                    matches.append(str(fpath.relative_to(version_path)))
            except (PermissionError, OSError):
                continue
    return matches


def compute_file_diff(content_a: str, content_b: str, path: str) -> dict:
    """Compute a unified diff between two file versions."""
    lines_a = content_a.splitlines(keepends=True)
    lines_b = content_b.splitlines(keepends=True)
    diff = list(difflib.unified_diff(lines_a, lines_b, fromfile=f"old/{path}", tofile=f"new/{path}", n=3))
    additions = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))
    return {
        "path": path,
        "additions": additions,
        "deletions": deletions,
        "changed": additions + deletions > 0,
        "diff_preview": "".join(diff[:50]) if diff else "",
    }


def analyze_version_pair(version_a: dict, version_b: dict, feature_terms: list[str]) -> dict:
    """Compare the feature between two versions."""
    files_a = set(find_feature_files(version_a["path"], feature_terms))
    files_b = set(find_feature_files(version_b["path"], feature_terms))

    added_files = sorted(files_b - files_a)
    removed_files = sorted(files_a - files_b)
    common_files = sorted(files_a & files_b)

    file_diffs = []
    for rel_path in common_files:
        path_a = version_a["path"] / rel_path
        path_b = version_b["path"] / rel_path
        try:
            content_a = path_a.read_text(encoding="utf-8", errors="ignore")
            content_b = path_b.read_text(encoding="utf-8", errors="ignore")
            diff_info = compute_file_diff(content_a, content_b, rel_path)
            if diff_info["changed"]:
                file_diffs.append(diff_info)
        except (PermissionError, OSError):
            continue

    return {
        "from_version": version_a["name"],
        "to_version": version_b["name"],
        "files_added": added_files,
        "files_removed": removed_files,
        "files_changed": [d["path"] for d in file_diffs],
        "total_additions": sum(d["additions"] for d in file_diffs),
        "total_deletions": sum(d["deletions"] for d in file_diffs),
        "change_magnitude": "NONE" if not file_diffs and not added_files and not removed_files
                            else "MINOR" if (len(file_diffs) <= 2 and not added_files and not removed_files)
                            else "MODERATE" if len(file_diffs) <= 5
                            else "MAJOR",
        "file_details": file_diffs,
    }


def select_canonical_version(versions: list[dict], feature_terms: list[str]) -> dict:
    """Select the most complete version of the feature."""
    scores = []
    for v in versions:
        files = find_feature_files(v["path"], feature_terms)
        scores.append({"version": v["name"], "feature_files": len(files), "path": str(v["path"])})

    scores.sort(key=lambda x: x["feature_files"], reverse=True)
    return {
        "canonical_version": scores[0] if scores else None,
        "ranking": scores,
        "rationale": "Version with the highest number of feature-related files selected as canonical.",
    }


def main():
    parser = argparse.ArgumentParser(description="Compare a feature across multiple legacy versions.")
    parser.add_argument("--root", required=True, help="Root directory containing version subdirectories")
    parser.add_argument("--feature", required=True, help="Feature name or description to compare")
    parser.add_argument("--output", default="version_diff.json", help="Output JSON file path")
    args = parser.parse_args()

    root_path = Path(args.root).resolve()
    if not root_path.exists():
        print(f"ERROR: Root path does not exist: {root_path}", file=sys.stderr)
        sys.exit(1)

    feature_terms = [
        args.feature,
        args.feature.lower(),
        args.feature.replace(" ", "_"),
        args.feature.replace(" ", "-"),
        "".join(word.capitalize() for word in args.feature.split()),
    ]
    feature_terms = list(dict.fromkeys(feature_terms))

    versions = discover_versions(root_path)
    print(f"🔍 Discovered {len(versions)} version directories under {root_path}")
    for v in versions:
        print(f"   - {v['name']} ({'versioned' if v['is_versioned'] else 'directory'})")

    if len(versions) < 2:
        print("⚠️  Less than 2 versions found. Nothing to compare.")

    canonical = select_canonical_version(versions, feature_terms)
    print(f"\n📌 Canonical version: {canonical['canonical_version']['version'] if canonical['canonical_version'] else 'none found'}")

    version_pairs = []
    for i in range(len(versions) - 1):
        pair_result = analyze_version_pair(versions[i], versions[i + 1], feature_terms)
        version_pairs.append(pair_result)
        print(f"   {versions[i]['name']} → {versions[i+1]['name']}: {pair_result['change_magnitude']} change")

    output = {
        "diff_metadata": {
            "analyzed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "root_path": str(root_path),
            "feature_name": args.feature,
            "versions_found": [v["name"] for v in versions],
        },
        "canonical_version": canonical,
        "version_evolution": version_pairs,
        "migration_recommendation": {
            "source": canonical["canonical_version"]["version"] if canonical["canonical_version"] else "unknown",
            "notes": (
                "Use the canonical version as primary migration source. "
                "Review MAJOR change pairs for any unique logic that must be preserved."
            ),
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\n✅ Version diff written to: {output_path}")


if __name__ == "__main__":
    main()
