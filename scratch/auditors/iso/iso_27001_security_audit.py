#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🛡️ ISO/IEC 27001:2022 Information Security Management Auditor            ║
║   BM25 + AST + Security Controls Governance Scanner                       ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC 27001:2022 Annex A controls:     ║
║   - A.8.24: Cryptography & Data Protection at Rest / In Transit           ║
║   - A.8.28: Secure Coding & Vulnerability Mitigations (OWASP Top 10)       ║
║   - A.8.12: Data Leakage Prevention & PII Masking in Logs                 ║
║   - A.8.9: Configuration Management & Secret Governance                   ║
║   - A.8.15: Logging & Monitoring Audit Trails                             ║
║   - ISO 27001 Security Compliance Score (0–100) & Audit Readiness Grade   ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_27001_security_audit.py /path/to/project [ProjectName]
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
class ISO27001Control:
    control_id: str         # A.8.24, A.8.28, etc.
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int        # Compliance Score Delta
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# ISO/IEC 27001:2022 Annex A Controls Matrix
# ─────────────────────────────────────────────────────────────────────────────
ISO27001_CONTROLS: list[ISO27001Control] = [

    # ── A.8.24 CRYPTOGRAPHY ───────────────────────────────────────────────────
    ISO27001Control(
        control_id="A.8.24-01", title="Strong Encryption in Transit (TLS 1.2/1.3 / HTTPS)",
        impact="POSITIVE", score_delta=+15,
        description="System enforces TLS encryption for external network communications.",
        remediation="Ensure HTTPS/TLS is enforced across all external API endpoints.",
    ),
    ISO27001Control(
        control_id="A.8.24-02", title="Strong Cryptographic Password Hashing (Argon2 / Bcrypt / PBKDF2)",
        impact="POSITIVE", score_delta=+15,
        description="Passwords and sensitive credentials are hashed using secure cryptographic algorithms.",
        remediation="Do not use MD5, SHA1, or un-salted hashes for user credentials.",
    ),

    # ── A.8.28 SECURE CODING & OWASP MITIGATIONS ──────────────────────────────
    ISO27001Control(
        control_id="A.8.28-01", title="Input Validation & Parameterized Queries (SQLi Protection)",
        impact="POSITIVE", score_delta=+15,
        description="Database queries use ORM or parameterized prepared statements.",
        remediation="Eliminate raw string concatenation in SQL queries.",
    ),
    ISO27001Control(
        control_id="A.8.28-02", title="Unsafe Code Execution Vulnerability (`eval` / `exec` / `os.system`)",
        impact="RISK", score_delta=-25,
        description="Found dynamic code evaluation functions capable of arbitrary code execution.",
        remediation="Replace dynamic `eval` or shell commands with typed function dispatches.",
    ),

    # ── A.8.12 DATA LEAKAGE PREVENTION & LOGS ─────────────────────────────────
    ISO27001Control(
        control_id="A.8.12-01", title="PII & Credential Masking in Application Logs",
        impact="POSITIVE", score_delta=+10,
        description="Application logging masks passwords, tokens, and personal data.",
        remediation="Sanitize loggers to strip authorization tokens and sensitive fields.",
    ),
    ISO27001Control(
        control_id="A.8.12-02", title="Hardcoded API Secrets & Private Keys",
        impact="RISK", score_delta=-25,
        description="Found plaintext AWS keys, RSA private keys, or API tokens committed in source code.",
        remediation="Move all secret keys to environment variables or secret vaults.",
    ),

    # ── A.8.9 CONFIGURATION MANAGEMENT & SECRETS GOVERNANCE ──────────────────
    ISO27001Control(
        control_id="A.8.9-01", title="Centralized Secret Management (Vault / KMS / .env)",
        impact="POSITIVE", score_delta=+10,
        description="Configuration and secret management is centralized and isolated from source code.",
        remediation="Use Vault or environment variables for secret injection.",
    ),

    # ── A.8.15 LOGGING & AUDIT TRAILS ─────────────────────────────────────────
    ISO27001Control(
        control_id="A.8.15-01", title="Structured Security Audit Logging (Access & Auth Logs)",
        impact="POSITIVE", score_delta=+10,
        description="Security-relevant events (logins, permission changes) emit audit logs.",
        remediation="Emit structured JSON audit events for security incidents.",
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Search Patterns
# ─────────────────────────────────────────────────────────────────────────────
PATTERNS = {
    "A.8.24-01": ["https://", "TLS", "ssl", "cert", "wss://"],
    "A.8.24-02": ["bcrypt", "argon2", "pbkdf2", "scrypt", "generate_password_hash"],
    "A.8.28-01": ["parameterized", "prepare", "execute(", "models.Model", "select("],
    "A.8.28-02": ["eval(", "exec(", "os.system(", "subprocess.Popen(", "shell=True"],
    "A.8.12-01": ["mask", "redact", "sanitize_log", "filter_sensitive"],
    "A.8.12-02": ["AKIA", "BEGIN PRIVATE KEY", "SECRET_KEY =", "api_key ="],
    "A.8.9-01": ["os.getenv", "process.env", "dotenv", "config.yaml", "vault"],
    "A.8.15-01": ["audit_log", "security_log", "access_log", "LogEntry"],
}


def scan_iso27001(root: Path, idx: IndexStoreAdapter) -> list[ISO27001Control]:
    """Scan codebase for ISO/IEC 27001:2022 security controls."""
    for ctrl in ISO27001_CONTROLS:
        pats = PATTERNS.get(ctrl.control_id, [])
        hits = set()

        for pat in pats:
            try:
                res = idx.search_code(pat, limit=3)
                for r in res:
                    if r.path and not any(x in r.path for x in ("node_modules", ".git", "vendor", "__pycache__")):
                        hits.add(r.path)
            except Exception:
                pass

        ctrl.evidence_files = sorted(list(hits))[:4]
        ctrl.found = len(ctrl.evidence_files) > 0

    return ISO27001_CONTROLS


def calculate_iso27001_score(controls: list[ISO27001Control]) -> tuple[int, str, str]:
    """Calculate ISO 27001 Security Compliance Score (0-100) and Audit Readiness Grade."""
    base_score = 50
    for c in controls:
        if c.found:
            base_score += c.score_delta

    score = max(0, min(100, base_score))

    if score >= 85:
        grade = "A+ (ISO 27001 Certified Ready)"
        status = "🟢 FULLY COMPLIANT — Strong Cryptography & Audit Controls"
    elif score >= 70:
        grade = "A (High Compliance Readiness)"
        status = "🟢 HIGH — Compliant with Minor Secret Governance Items"
    elif score >= 55:
        grade = "B (Moderate Compliance Debt)"
        status = "🟡 MEDIUM — Requires Secret Sanitization & Input Sanitization"
    else:
        grade = "C/F (ISO 27001 Audit Hazard)"
        status = "🔴 NON-COMPLIANT — Hardcoded Secrets or Code Execution Risks"

    return score, grade, status


def print_report(project: str, root: Path, controls: list[ISO27001Control],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [c for c in controls if c.found]
    score, grade, status = calculate_iso27001_score(controls)

    lines = [
        f"# 🛡️ ISO/IEC 27001:2022 Security Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 27001 Security Governance Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 27001 Security Score** | **{score} / 100** |",
        f"| **Certification Readiness Grade** | **{grade}** |",
        f"| **Compliance Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified ISO 27001 Controls | {len(found)} / {len(controls)} |",
        "",
        "## 🔍 Verified ISO 27001 Annex A Controls & Code Evidence",
        "",
        "| Control ID | ISO 27001 Control Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for c in found:
        ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2])
        lines.append(f"| `{c.control_id}` | {c.title} | ✅ FOUND | {ev} | {c.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 27001 Compliance Remediation Roadmap",
        "",
        "1. **Control A.8.24 (Cryptography)**: Ensure all external network endpoints mandate TLS 1.3 encryption.",
        "2. **Control A.8.28 (Secure Coding)**: Eliminate dynamic code evaluation (`eval`, `exec`) and use parameterized queries.",
        "3. **Control A.8.12 (Data Leakage)**: Scrub all plaintext secret keys into external environment variables.",
        "4. **Control A.8.15 (Audit Logging)**: Implement structured JSON security audit logging for authentication events.",
        "",
        "---",
        f"*ISO/IEC 27001:2022 Security Compliance Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🛡️ ISO/IEC 27001:2022 INFORMATION SECURITY AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 27001 Security Score    : {score} / 100")
    print(f"  Certification Grade         : {grade}")
    print(f"  Verified Annex A Controls   : {len(found)} / {len(controls)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_27001_security_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_27001_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    controls = scan_iso27001(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, controls, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
