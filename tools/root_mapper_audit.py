#!/usr/bin/env python3
"""
Root Mapper + Audit Script
Purpose:
- Scan an entire build root
- Produce a structural map
- Audit architecture signals
- Surface implementation clues for the next build phase
- Generate machine-readable JSON + human-readable Markdown reports

Usage:
    python tools/root_mapper_audit.py
    python tools/root_mapper_audit.py --root .
    python tools/root_mapper_audit.py --max-file-read-bytes 200000
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_IGNORE_DIRS = {
    ".git",
    ".next",
    ".turbo",
    ".cache",
    ".cursor",
    ".idea",
    ".vscode",
    ".DS_Store",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".venv",
    "venv",
    "tmp",
    "temp",
    ".netlify",
}

TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".txt", ".yaml", ".yml",
    ".toml", ".ini", ".env", ".env.example", ".sql", ".html", ".css", ".scss",
    ".sh", ".ps1", ".mjs", ".cjs", ".xml"
}

KEY_FILENAMES = {
    "package.json",
    "vite.config.ts",
    "vite.config.js",
    "netlify.toml",
    "supabase.toml",
    "tsconfig.json",
    ".env",
    ".env.example",
    "README.md",
    "NEXT_THREAD_PROMPT.md",
    "BUILD_TRACKING.md",
    "docker-compose.yml",
    "Dockerfile",
}

AI_HINT_PATTERNS = [
    r"\bopenai\b",
    r"\bembeddings?\b",
    r"\bvector\b",
    r"\bpgvector\b",
    r"\brag\b",
    r"\bsemantic\b",
    r"\bretriev",
    r"\bingest",
    r"\bchunk",
    r"\bq&a\b",
    r"\bassistant\b",
    r"\bllm\b",
    r"\bprompt\b",
    r"\bknowledge\s*base\b",
]

INGESTION_HINT_PATTERNS = [
    r"\bpymupdf\b",
    r"\bpdfplumber\b",
    r"\bpypdf\b",
    r"\bunstructured\b",
    r"\btextract\b",
    r"\bocr\b",
    r"\bchunk\b",
    r"\btoken\b",
    r"\bembedding\b",
    r"\bvector\b",
    r"\bindex\b",
    r"\bsearch\b",
]

AUTH_HINT_PATTERNS = [
    r"\bsupabase\b",
    r"\boauth\b",
    r"\bjwt\b",
    r"\brbac\b",
    r"\bauth\b",
    r"\bgoogle\s*oauth\b",
]

FRONTEND_HINT_PATTERNS = [
    r"\breact\b",
    r"\bvite\b",
    r"\btsx\b",
    r"\broute\b",
    r"\bcomponent\b",
]

BACKEND_HINT_PATTERNS = [
    r"\bnetlify/functions\b",
    r"\bexpress\b",
    r"\bapi\b",
    r"\bserverless\b",
    r"\bhandler\b",
]

DB_HINT_PATTERNS = [
    r"\bpostgres\b",
    r"\bneon\b",
    r"\bprisma\b",
    r"\bsql\b",
    r"\bmigration\b",
    r"\bpg\b",
]

TRACKING_HINT_PATTERNS = [
    r"\btracking\b",
    r"\bbuild\s*plan\b",
    r"\bphase\b",
    r"\broadmap\b",
    r"\bnext[_\s-]*thread\b",
    r"\bhandoff\b",
    r"\baudit\b",
    r"\bmapper\b",
]


@dataclass
class FileRecord:
    path: str
    relative_path: str
    extension: str
    size_bytes: int
    line_count: Optional[int]
    sha256_first_64k: str
    is_text: bool
    signals: List[str]


def sha256_first_chunk(path: Path, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            h.update(f.read(chunk_size))
        return h.hexdigest()
    except Exception:
        return "ERROR"


def safe_read_text(path: Path, max_bytes: int) -> Optional[str]:
    try:
        if path.stat().st_size > max_bytes:
            with path.open("rb") as f:
                raw = f.read(max_bytes)
            return raw.decode("utf-8", errors="ignore")
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


def count_lines(text: Optional[str]) -> Optional[int]:
    if text is None:
        return None
    return text.count("\n") + 1 if text else 0


def should_ignore(path: Path) -> bool:
    return any(part in DEFAULT_IGNORE_DIRS for part in path.parts)


def looks_textual(path: Path) -> bool:
    if path.name in {".env", ".env.example"}:
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS


def find_signals(text: str) -> List[str]:
    text_low = text.lower()
    found = set()

    def scan(patterns: List[str], label: str) -> None:
        for p in patterns:
            if re.search(p, text_low):
                found.add(label)
                return

    scan(AI_HINT_PATTERNS, "ai")
    scan(INGESTION_HINT_PATTERNS, "ingestion")
    scan(AUTH_HINT_PATTERNS, "auth")
    scan(FRONTEND_HINT_PATTERNS, "frontend")
    scan(BACKEND_HINT_PATTERNS, "backend")
    scan(DB_HINT_PATTERNS, "database")
    scan(TRACKING_HINT_PATTERNS, "tracking")
    return sorted(found)


def parse_package_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {
            "name": data.get("name"),
            "version": data.get("version"),
            "scripts": data.get("scripts", {}),
            "dependencies": data.get("dependencies", {}),
            "devDependencies": data.get("devDependencies", {}),
        }
    except Exception as e:
        return {"error": str(e)}


def detect_api_routes(files: List[FileRecord]) -> List[str]:
    routes = []
    for f in files:
        rel = f.relative_path.replace("\\", "/")
        if "netlify/functions/" in rel or rel.startswith("api/") or "/api/" in rel:
            routes.append(rel)
    return sorted(routes)


def detect_tracking_docs(files: List[FileRecord]) -> List[str]:
    matches = []
    for f in files:
        rel = f.relative_path.lower()
        if any(k in rel for k in ["tracking", "handoff", "next_thread", "roadmap", "build_plan", "audit", "mapper"]):
            matches.append(f.relative_path)
    return sorted(matches)


def detect_docs(files: List[FileRecord]) -> List[str]:
    docs = []
    for f in files:
        rel = f.relative_path.lower()
        if f.extension in {".md", ".txt"}:
            docs.append(f.relative_path)
    return sorted(docs)


def classify_zone(path_str: str) -> str:
    rel = path_str.replace("\\", "/").lower()
    if any(x in rel for x in ["src/", "components/", "pages/", "app/"]):
        return "frontend"
    if any(x in rel for x in ["netlify/functions/", "api/", "server/", "backend/"]):
        return "backend"
    if any(x in rel for x in ["sql/", "migrations/", "db/", "database/"]):
        return "database"
    if any(x in rel for x in ["tracking/", "docs/", "roadmap/", "handoff/"]):
        return "tracking_docs"
    if any(x in rel for x in ["tools/", "scripts/"]):
        return "tooling"
    return "other"


def detect_env_var_refs(text: str) -> List[str]:
    patterns = [
        r"process\.env\.([A-Z0-9_]+)",
        r"import\.meta\.env\.([A-Z0-9_]+)",
        r"os\.environ(?:\.get)?\(['\"]([A-Z0-9_]+)['\"]\)",
        r"os\.getenv\(['\"]([A-Z0-9_]+)['\"]\)",
    ]
    refs = set()
    for p in patterns:
        for match in re.findall(p, text):
            refs.add(match)
    return sorted(refs)


def summarize_dir_sizes(file_records: List[FileRecord]) -> Dict[str, int]:
    totals = defaultdict(int)
    for f in file_records:
        parts = Path(f.relative_path).parts
        if not parts:
            continue
        root_dir = parts[0]
        totals[root_dir] += f.size_bytes
    return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))


def build_tree(root: Path) -> Dict[str, Any]:
    def walk_dir(d: Path) -> Dict[str, Any]:
        node = {"name": d.name, "type": "dir", "children": []}
        try:
            children = sorted(d.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except Exception:
            return node

        for child in children:
            if should_ignore(child):
                continue
            if child.is_dir():
                node["children"].append(walk_dir(child))
            else:
                node["children"].append({
                    "name": child.name,
                    "type": "file",
                    "size_bytes": child.stat().st_size if child.exists() else 0
                })
        return node

    return walk_dir(root)


def collect_files(root: Path, max_file_read_bytes: int) -> Tuple[List[FileRecord], Dict[str, Any]]:
    file_records: List[FileRecord] = []
    env_refs = defaultdict(set)
    file_signal_counts = Counter()
    empty_dirs = []

    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)

        dirnames[:] = [d for d in dirnames if d not in DEFAULT_IGNORE_DIRS]

        rel_current = current.relative_to(root)
        if rel_current != Path("."):
            try:
                if not any((current / d).exists() for d in dirnames) and not filenames:
                    empty_dirs.append(str(rel_current))
            except Exception:
                pass

        for filename in filenames:
            path = current / filename
            if should_ignore(path):
                continue

            try:
                size = path.stat().st_size
            except Exception:
                continue

            is_text = looks_textual(path)
            text = safe_read_text(path, max_file_read_bytes) if is_text else None
            lc = count_lines(text)

            signals = []
            if text:
                signals = find_signals(text)
                for s in signals:
                    file_signal_counts[s] += 1
                for env_var in detect_env_var_refs(text):
                    env_refs[env_var].add(str(path.relative_to(root)))

            rec = FileRecord(
                path=str(path),
                relative_path=str(path.relative_to(root)),
                extension=path.suffix.lower(),
                size_bytes=size,
                line_count=lc,
                sha256_first_64k=sha256_first_chunk(path),
                is_text=is_text,
                signals=signals,
            )
            file_records.append(rec)

    aux = {
        "env_var_refs": {k: sorted(v) for k, v in sorted(env_refs.items())},
        "file_signal_counts": dict(file_signal_counts),
        "empty_dirs": sorted(empty_dirs),
    }
    return file_records, aux


def score_readiness(files: List[FileRecord], package_data: Dict[str, Any], api_routes: List[str]) -> Dict[str, Any]:
    rels = {f.relative_path.replace("\\", "/").lower() for f in files}
    deps = set()
    for group in ("dependencies", "devDependencies"):
        if group in package_data and isinstance(package_data[group], dict):
            deps.update(k.lower() for k in package_data[group].keys())

    scores = {}

    frontend_score = 0
    if any("src/" in p or p.endswith(".tsx") or p.endswith(".jsx") for p in rels):
        frontend_score += 30
    if "react" in deps:
        frontend_score += 30
    if "vite" in deps or any("vite.config." in p for p in rels):
        frontend_score += 20
    if any("components/" in p for p in rels):
        frontend_score += 20
    scores["frontend"] = min(frontend_score, 100)

    backend_score = 0
    if api_routes:
        backend_score += 40
    if any("netlify/functions/" in p for p in rels):
        backend_score += 30
    if any(p.endswith(".sql") for p in rels):
        backend_score += 10
    if any("api/" in p or "server/" in p for p in rels):
        backend_score += 20
    scores["backend"] = min(backend_score, 100)

    auth_score = 0
    if "supabase" in deps:
        auth_score += 40
    if any("auth" in p for p in rels):
        auth_score += 20
    if any("rbac" in p for p in rels):
        auth_score += 20
    if any("google" in p and "oauth" in p for p in rels):
        auth_score += 20
    scores["auth"] = min(auth_score, 100)

    ingestion_score = 0
    if any("ingest" in p or "rag" in p or "vector" in p or "embedding" in p for p in rels):
        ingestion_score += 40
    if any("openai" in d or "langchain" in d or "pgvector" in d for d in deps):
        ingestion_score += 30
    if any("pdf" in p.lower() for p in rels):
        ingestion_score += 10
    if any("search" in p.lower() or "assistant" in p.lower() for p in rels):
        ingestion_score += 20
    scores["ingestion_ai"] = min(ingestion_score, 100)

    tracking_score = 0
    if any("tracking/" in p for p in rels):
        tracking_score += 40
    if any("next_thread" in p or "handoff" in p or "roadmap" in p for p in rels):
        tracking_score += 40
    if any(p.endswith(".md") for p in rels):
        tracking_score += 20
    scores["tracking"] = min(tracking_score, 100)

    return scores


def detect_duplicate_filenames(files: List[FileRecord]) -> Dict[str, List[str]]:
    by_name = defaultdict(list)
    for f in files:
        by_name[Path(f.relative_path).name].append(f.relative_path)
    return {k: v for k, v in by_name.items() if len(v) > 1}


def detect_large_files(files: List[FileRecord], min_mb: float = 1.0) -> List[Dict[str, Any]]:
    threshold = int(min_mb * 1024 * 1024)
    out = []
    for f in sorted(files, key=lambda x: x.size_bytes, reverse=True):
        if f.size_bytes >= threshold:
            out.append({
                "relative_path": f.relative_path,
                "size_bytes": f.size_bytes,
                "size_mb": round(f.size_bytes / (1024 * 1024), 2),
            })
    return out


def detect_dead_zone_candidates(files: List[FileRecord]) -> List[Dict[str, Any]]:
    suspects = []
    for f in files:
        rel = f.relative_path.replace("\\", "/").lower()
        if f.is_text and f.line_count is not None:
            if f.line_count <= 3 and f.size_bytes < 200 and any(
                rel.endswith(ext) for ext in [".ts", ".tsx", ".js", ".jsx", ".py", ".sql"]
            ):
                suspects.append({
                    "relative_path": f.relative_path,
                    "line_count": f.line_count,
                    "size_bytes": f.size_bytes,
                    "reason": "tiny source file",
                })
        if "todo" in rel or "stub" in rel or "placeholder" in rel:
            suspects.append({
                "relative_path": f.relative_path,
                "line_count": f.line_count,
                "size_bytes": f.size_bytes,
                "reason": "naming suggests incomplete work",
            })
    return suspects


def generate_markdown_report(
    root: Path,
    files: List[FileRecord],
    tree: Dict[str, Any],
    package_data: Dict[str, Any],
    aux: Dict[str, Any],
    api_routes: List[str],
    tracking_docs: List[str],
    docs: List[str],
    readiness: Dict[str, Any],
    duplicates: Dict[str, List[str]],
    large_files: List[Dict[str, Any]],
    dead_zones: List[Dict[str, Any]],
    dir_sizes: Dict[str, int],
) -> str:
    ext_counts = Counter(f.extension or "[no_ext]" for f in files)
    zone_counts = Counter(classify_zone(f.relative_path) for f in files)
    total_size = sum(f.size_bytes for f in files)

    lines = []
    lines.append(f"# Root Build Audit Report")
    lines.append("")
    lines.append(f"**Root:** `{root}`")
    lines.append(f"**Files scanned:** {len(files)}")
    lines.append(f"**Total size:** {round(total_size / (1024 * 1024), 2)} MB")
    lines.append("")

    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- Frontend readiness: **{readiness.get('frontend', 0)}/100**")
    lines.append(f"- Backend readiness: **{readiness.get('backend', 0)}/100**")
    lines.append(f"- Auth readiness: **{readiness.get('auth', 0)}/100**")
    lines.append(f"- Ingestion / AI readiness: **{readiness.get('ingestion_ai', 0)}/100**")
    lines.append(f"- Tracking / handoff readiness: **{readiness.get('tracking', 0)}/100**")
    lines.append("")

    lines.append("## Key Findings")
    lines.append("")
    lines.append(f"- API route candidates found: **{len(api_routes)}**")
    lines.append(f"- Tracking / handoff docs found: **{len(tracking_docs)}**")
    lines.append(f"- Environment variable references found: **{len(aux.get('env_var_refs', {}))}**")
    lines.append(f"- Duplicate filenames found: **{len(duplicates)}**")
    lines.append(f"- Large files found: **{len(large_files)}**")
    lines.append(f"- Dead-zone candidates found: **{len(dead_zones)}**")
    lines.append(f"- Empty directories found: **{len(aux.get('empty_dirs', []))}**")
    lines.append("")

    if package_data:
        lines.append("## package.json Summary")
        lines.append("")
        if package_data.get("error"):
            lines.append(f"- Error: `{package_data['error']}`")
        else:
            lines.append(f"- Name: `{package_data.get('name')}`")
            lines.append(f"- Version: `{package_data.get('version')}`")
            scripts = package_data.get("scripts", {})
            if scripts:
                lines.append("- Scripts:")
                for k, v in scripts.items():
                    lines.append(f"  - `{k}` → `{v}`")
            deps = package_data.get("dependencies", {})
            devdeps = package_data.get("devDependencies", {})
            if deps:
                lines.append(f"- Runtime deps ({len(deps)}): {', '.join(sorted(deps.keys())[:25])}")
            if devdeps:
                lines.append(f"- Dev deps ({len(devdeps)}): {', '.join(sorted(devdeps.keys())[:25])}")
        lines.append("")

    lines.append("## Directory Size Breakdown")
    lines.append("")
    for d, size in list(dir_sizes.items())[:20]:
        lines.append(f"- `{d}`: {round(size / (1024 * 1024), 2)} MB")
    lines.append("")

    lines.append("## File Extension Breakdown")
    lines.append("")
    for ext, count in ext_counts.most_common(20):
        lines.append(f"- `{ext}`: {count}")
    lines.append("")

    lines.append("## Zone Breakdown")
    lines.append("")
    for zone, count in zone_counts.most_common():
        lines.append(f"- `{zone}`: {count}")
    lines.append("")

    if api_routes:
        lines.append("## API Routes / Backend Entry Candidates")
        lines.append("")
        for route in api_routes[:100]:
            lines.append(f"- `{route}`")
        lines.append("")

    if tracking_docs:
        lines.append("## Tracking / Handoff / Build Docs")
        lines.append("")
        for doc in tracking_docs[:100]:
            lines.append(f"- `{doc}`")
        lines.append("")

    if docs:
        lines.append("## Documentation Files")
        lines.append("")
        for doc in docs[:100]:
            lines.append(f"- `{doc}`")
        lines.append("")

    env_refs = aux.get("env_var_refs", {})
    if env_refs:
        lines.append("## Environment Variable References")
        lines.append("")
        for var, paths in list(env_refs.items())[:100]:
            lines.append(f"- `{var}`")
            for p in paths[:10]:
                lines.append(f"  - `{p}`")
        lines.append("")

    if duplicates:
        lines.append("## Duplicate Filenames")
        lines.append("")
        for name, paths in list(sorted(duplicates.items()))[:100]:
            lines.append(f"- `{name}`")
            for p in paths:
                lines.append(f"  - `{p}`")
        lines.append("")

    if large_files:
        lines.append("## Large Files")
        lines.append("")
        for item in large_files[:100]:
            lines.append(f"- `{item['relative_path']}` — {item['size_mb']} MB")
        lines.append("")

    if dead_zones:
        lines.append("## Dead-Zone / Stub Candidates")
        lines.append("")
        for item in dead_zones[:100]:
            lines.append(
                f"- `{item['relative_path']}` — {item['reason']} "
                f"(lines={item.get('line_count')}, bytes={item.get('size_bytes')})"
            )
        lines.append("")

    if aux.get("empty_dirs"):
        lines.append("## Empty Directories")
        lines.append("")
        for d in aux["empty_dirs"][:100]:
            lines.append(f"- `{d}`")
        lines.append("")

    lines.append("## Signal Counts")
    lines.append("")
    for sig, count in sorted(aux.get("file_signal_counts", {}).items()):
        lines.append(f"- `{sig}`: {count}")
    lines.append("")

    lines.append("## Build Direction Recommendations")
    lines.append("")
    recommendations = []

    if readiness.get("ingestion_ai", 0) < 50:
        recommendations.append("Create a dedicated ingestion pipeline module before building the regulation Q&A layer.")
    if readiness.get("tracking", 0) < 70:
        recommendations.append("Strengthen tracking/handoff structure so future AI threads can resume deterministically.")
    if readiness.get("backend", 0) < 60:
        recommendations.append("Stabilize backend route structure before adding AI services.")
    if readiness.get("auth", 0) >= 60:
        recommendations.append("Leverage existing auth/RBAC infrastructure to gate regulation content and assistant actions.")
    if not recommendations:
        recommendations.append("Current build appears ready for a regulation-ingestion assistant prototype.")

    for rec in recommendations:
        lines.append(f"- {rec}")
    lines.append("")

    lines.append("## Suggested Next Build Modules")
    lines.append("")
    lines.append("- `ingestion/` — handbook parsing, chunking, normalization, metadata enrichment")
    lines.append("- `knowledge/` — source registry, citation store, handbook versions")
    lines.append("- `retrieval/` — embeddings, vector search, lexical fallback, reranking")
    lines.append("- `assistant/` — answer orchestration, citation formatting, guardrails")
    lines.append("- `compliance/` — source trust scoring, effective-date validation, policy versioning")
    lines.append("- `tracking/` — deterministic build state, upgrade logs, next-thread protocol")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Project root to scan")
    parser.add_argument("--max-file-read-bytes", type=int, default=200_000)
    parser.add_argument("--output-dir", default="tracking/reports")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output_dir = root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    files, aux = collect_files(root, args.max_file_read_bytes)
    tree = build_tree(root)

    package_json_path = root / "package.json"
    package_data = parse_package_json(package_json_path) if package_json_path.exists() else {}

    api_routes = detect_api_routes(files)
    tracking_docs = detect_tracking_docs(files)
    docs = detect_docs(files)
    readiness = score_readiness(files, package_data, api_routes)
    duplicates = detect_duplicate_filenames(files)
    large_files = detect_large_files(files, min_mb=1.0)
    dead_zones = detect_dead_zone_candidates(files)
    dir_sizes = summarize_dir_sizes(files)

    root_map = {
        "root": str(root),
        "tree": tree,
    }

    root_audit = {
        "root": str(root),
        "summary": {
            "file_count": len(files),
            "total_size_bytes": sum(f.size_bytes for f in files),
            "readiness": readiness,
        },
        "files": [asdict(f) for f in files],
        "package_json": package_data,
        "api_routes": api_routes,
        "tracking_docs": tracking_docs,
        "docs": docs,
        "env_var_refs": aux.get("env_var_refs", {}),
        "file_signal_counts": aux.get("file_signal_counts", {}),
        "duplicate_filenames": duplicates,
        "large_files": large_files,
        "dead_zone_candidates": dead_zones,
        "empty_dirs": aux.get("empty_dirs", []),
        "dir_sizes": dir_sizes,
    }

    markdown = generate_markdown_report(
        root=root,
        files=files,
        tree=tree,
        package_data=package_data,
        aux=aux,
        api_routes=api_routes,
        tracking_docs=tracking_docs,
        docs=docs,
        readiness=readiness,
        duplicates=duplicates,
        large_files=large_files,
        dead_zones=dead_zones,
        dir_sizes=dir_sizes,
    )

    (output_dir / "root_map.json").write_text(json.dumps(root_map, indent=2), encoding="utf-8")
    (output_dir / "root_audit.json").write_text(json.dumps(root_audit, indent=2), encoding="utf-8")
    (output_dir / "root_audit.md").write_text(markdown, encoding="utf-8")

    print("Audit complete.")
    print(f"Wrote: {output_dir / 'root_map.json'}")
    print(f"Wrote: {output_dir / 'root_audit.json'}")
    print(f"Wrote: {output_dir / 'root_audit.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
