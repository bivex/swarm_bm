#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🔍 ISO Open Data Fast Search CLI Engine                                 ║
║   Query 80,000+ ISO Standards by Keyword, Code, ICS or Domain Category    ║
║                                                                           ║
║   EXAMPLES:                                                               ║
║     python3 scratch/auditors/iso/iso_search.py "27001"                   ║
║     python3 scratch/auditors/iso/iso_search.py "UI UX"                    ║
║     python3 scratch/auditors/iso/iso_search.py --category security        ║
║     python3 scratch/auditors/iso/iso_search.py "usability" --json         ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_search.py <QUERY> [--category CAT] [--limit N] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

CACHE_DIR = Path.home() / ".cache" / "iso_open_data"
CACHE_FILE = CACHE_DIR / "iso_deliverables_cache.json"

# Category Shortcuts Dictionary
CATEGORIES = {
    "ui": ["9241", "usability", "ergonomics", "human-centred", "interface", "user experience", "accessibility", "25066", "30071"],
    "security": ["27001", "27002", "27005", "27017", "27018", "27034", "27035", "27036", "27040", "15408", "62443", "cybersecurity"],
    "quality": ["25010", "9001", "8000", "quality management", "software quality", "square"],
    "privacy": ["27701", "privacy", "pii", "gdpr", "personal data"],
    "ai": ["42001", "23053", "artificial intelligence", "machine learning"],
    "automotive": ["26262", "road vehicles", "functional safety", "asil"],
    "medtech": ["13485", "62366", "medical devices"],
    "cloud": ["27017", "27018", "cloud services", "virtualization"],
    "resilience": ["22301", "business continuity", "disaster recovery"],
}


def load_iso_cache() -> dict[str, dict[str, Any]]:
    """Load ISO standards dataset from local cache."""
    if not CACHE_FILE.exists():
        print("❌ Cache not found. Generating reference directory...")
        return {}

    try:
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        return data.get("standards", {})
    except Exception as e:
        print(f"❌ Failed loading cache: {e}")
        return {}


def search_standards(query: str = "", category: str = "", limit: int = 20) -> list[dict[str, Any]]:
    """Search ISO standards by query, category keywords or ICS codes."""
    standards = load_iso_cache()
    if not standards:
        return []

    query_tokens = [q.lower().strip() for q in re.findall(r"\w+", query)] if query else []
    cat_keywords = CATEGORIES.get(category.lower(), [category.lower()]) if category else []

    results = []

    for ref, item in standards.items():
        ref_lower = ref.lower()
        title_en = (item.get("title_en") or "").lower()
        ics_list = [str(c).lower() for c in (item.get("ics_code") or [])]
        tc = (item.get("owner_committee") or "").lower()

        # Check Category Match
        if cat_keywords:
            if not any(kw in ref_lower or kw in title_en or any(kw in ics for ics in ics_list) for kw in cat_keywords):
                continue

        # Check Query Match
        if query_tokens:
            match = True
            for tok in query_tokens:
                if tok not in ref_lower and tok not in title_en and tok not in tc and not any(tok in ics for ics in ics_list):
                    match = False
                    break
            if not match:
                continue

        results.append(item)

    # Sort by exact reference
    results.sort(key=lambda x: x.get("reference", ""))
    return results[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description="ISO Open Data Fast Search CLI Engine")
    parser.add_argument("query", nargs="?", default="", help="Search query string (e.g. 27001, 'UI UX', usability)")
    parser.add_argument("--category", "-c", default="", help="Category filter (ui, security, quality, privacy, ai, automotive, medtech, cloud, resilience)")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Maximum number of results to display (default: 20)")
    parser.add_argument("--json", action="store_true", help="Output results as raw JSON")

    args = parser.parse_args()

    t0 = time.perf_counter()
    results = search_standards(query=args.query, category=args.category, limit=args.limit)
    elapsed = time.perf_counter() - t0

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    SEP = "═" * 80
    print(f"\n{SEP}")
    print(f"  🔍 ISO OPEN DATA SEARCH RESULTS ({len(results)} matches in {elapsed:.3f}s)")
    print(SEP)

    if not results:
        print("  ⚪ No matching ISO standards found.")
        print(f"{SEP}\n")
        return

    for idx, item in enumerate(results, 1):
        ref = item.get("reference", "N/A")
        title = item.get("title_en") or item.get("title_fr") or "No title"
        date_pub = item.get("publication_date") or "N/A"
        edition = item.get("edition") or 1
        ics = ", ".join(item.get("ics_code") or ["N/A"])
        tc = item.get("owner_committee") or "N/A"
        stage = item.get("current_stage") or 6060

        print(f"  {idx:2d}. 📜 {ref}")
        print(f"      Title     : {title}")
        print(f"      Published : {date_pub} (Edition {edition}) | Stage: {stage}")
        print(f"      ICS Codes : {ics} | Committee: {tc}")
        print("  " + "─" * 76)

    print(f"{SEP}\n")


if __name__ == "__main__":
    main()
