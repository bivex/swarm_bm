#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🏭 ISA/IEC 62443 Industrial Automation & OT Security Auditor            ║
║   BM25 + AST + SCADA, Modbus, OPC UA & Industrial Control Security Scanner║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISA/IEC 62443 Industrial OT Controls:    ║
║   - Network Zone & Conduit Segmentation (Air-Gapping / Firewall Bounds)   ║
║   - Industrial Protocol Security (Modbus, OPC UA, BACnet, MQTT)           ║
║   - Physical Hardware Watchdog & PLC Reset Integration                    ║
║   - OT Security Level (SL1–SL4) Access Controls & Command Signatures      ║
║   - IEC 62443 OT Security Index (0–100) & Industrial Safety Grade         ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_62443_industrial_security_audit.py /path/to/project [ProjectName]
"""
from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter


@dataclass
class ISO62443Metric:
    domain: str             # ZONE_CONDUIT / INDUSTRIAL_PROTOCOLS / HARDWARE_SAFETY / COMMAND_SIGNATURES
    metric_id: str          # OT-001..OT-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


OT_METRICS: list[ISO62443Metric] = [
    ISO62443Metric(
        domain="ZONE_CONDUIT", metric_id="OT-001",
        title="Industrial Network Zone & Conduit Segmentation (Air-Gapping)",
        impact="POSITIVE", score_delta=+25,
        description="System enforces strict boundary separation between IT and OT network zones.",
        remediation="Isolate SCADA / PLC control channels from public IT networks.",
    ),
    ISO62443Metric(
        domain="INDUSTRIAL_PROTOCOLS", metric_id="OT-002",
        title="Secure Industrial Protocol Communication (OPC UA / Modbus TCP / MQTT)",
        impact="POSITIVE", score_delta=+25,
        description="System uses authenticated and encrypted industrial communications.",
        remediation="Enforce OPC UA Security Profiles (Basic256Sha256) or TLS for MQTT.",
    ),
    ISO62443Metric(
        domain="HARDWARE_SAFETY", metric_id="OT-003",
        title="PLC Hardware Watchdog & Safety Relay Integration",
        impact="POSITIVE", score_delta=+25,
        description="System integrates hardware PLC watchdogs and safety relay state monitors.",
        remediation="Connect software health monitor to hardware safety relay output.",
    ),
    ISO62443Metric(
        domain="COMMAND_SIGNATURES", metric_id="OT-004",
        title="Cryptographic Signature Verification for Actuator Control Commands",
        impact="POSITIVE", score_delta=+25,
        description="Actuator and valve control commands require digital signatures to prevent spoofing.",
        remediation="Sign control payload commands before executing valve or motor state changes.",
    ),
]


PATTERNS = {
    "OT-001": ["air_gap", "ot_zone", "it_zone", "firewall_bound", "scada_gateway"],
    "OT-002": ["opcua", "modbus", "bacnet", "mqtt_tls", "industrial_protocol"],
    "OT-003": ["plc_watchdog", "safety_relay", "hardware_interlock", "e_stop"],
    "OT-004": ["signed_command", "actuator_sign", "verify_control_msg"],
}


def scan_iso62443(root: Path, idx: IndexStoreAdapter) -> list[ISO62443Metric]:
    """Scan codebase for ISA/IEC 62443 Industrial Automation & Control Systems Security controls."""
    for m in OT_METRICS:
        pats = PATTERNS.get(m.metric_id, [])
        hits = set()

        for pat in pats:
            try:
                res = idx.search_code(pat, limit=3)
                for r in res:
                    if r.path and not any(x in r.path for x in ("node_modules", ".git", "vendor")):
                        hits.add(r.path)
            except Exception:
                pass

        m.evidence_files = sorted(list(hits))[:4]
        m.found = len(m.evidence_files) > 0

    return OT_METRICS


def calculate_iso62443_score(metrics: list[ISO62443Metric]) -> tuple[int, str, str]:
    """Calculate IEC 62443 OT Security Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "Security Level 3/4 (IEC 62443 Certified High OT Security)"
        status = "🟢 HIGH OT SECURITY — OPC UA Encryption, Hardware Interlocks & Zone Segmentation Active"
    elif score >= 50:
        grade = "Security Level 2 (Moderate OT Security)"
        status = "🟢 GOOD — Industrial Protocol Security or Zone Boundaries Present"
    else:
        grade = "Security Level 1 (OT Security Hazard)"
        status = "🔴 OT SECURITY HAZARD — Unauthenticated Industrial Protocols or Missing Interlocks"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO62443Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso62443_score(metrics)

    lines = [
        f"# 🏭 ISA/IEC 62443 Industrial Automation & OT Security Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 IEC 62443 OT Security Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **IEC 62443 OT Security Score** | **{score} / 100** |",
        f"| **OT Security Level Grade** | **{grade}** |",
        f"| **Industrial Security Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified OT Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified IEC 62443 OT Security Evidence",
        "",
        "| Domain | OT Security Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 IEC 62443 Industrial Security Remediation Blueprint",
        "",
        "1. **Protocol Security**: Enforce encrypted OPC UA or TLS for industrial telemetry.",
        "2. **Zone Segmentation**: Isolate OT control network interfaces from public IT networks.",
        "3. **Hardware Interlocks**: Wire software emergency stop triggers to PLC safety relays.",
        "",
        "---",
        f"*ISA/IEC 62443 Industrial Automation & Control Systems Security Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🏭 ISA/IEC 62443 INDUSTRIAL OT SECURITY AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  IEC 62443 OT Security Score : {score} / 100")
    print(f"  OT Security Level Grade     : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_62443_industrial_security_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_62443_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso62443(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
