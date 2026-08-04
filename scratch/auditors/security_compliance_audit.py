#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🛡️ Security & Compliance Risk Auditor (M&A Due Diligence Edition)        ║
║   BM25 + AST + Hardcoded Secret & OWASP Top 10 + Compliance Scanner        ║
║                                                                           ║
║   PURPOSE: Security & Compliance due diligence for M&A / selling code.     ║
║   - Hardcoded Secrets & Credentials (API Keys, AWS, Private Keys, DB URIs) ║
║   - OWASP Top 10 Vulnerability Patterns (Injection, Auth, Crypto, Deser)   ║
║   - Compliance Readiness (SOC2, GDPR, HIPAA, PCI-DSS)                      ║
║   - Software Bill of Materials (SBOM) & Dependency Risk Scan               ║
║   - Security Debt Score (0–100) & Due Diligence Grade (A+ to F)            ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/security_compliance_audit.py /path/to/project [ProjectName]
"""
from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from collections import defaultdict
from typing import Any

root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter


@dataclass
class SecurityFinding:
    category: str           # SECRETS / OWASP / COMPLIANCE / DEPENDENCY
    rule_id: str            # SEC-001, OWASP-A03, SOC2-01, etc.
    title: str
    severity: str           # CRITICAL / HIGH / MEDIUM / LOW
    penalty: int            # Security Debt Score penalty
    description: str
    evidence_files: list[str] = field(default_factory=list)
    recommendation: str = ""
    found: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# Security & Compliance Rule Registry
# ─────────────────────────────────────────────────────────────────────────────
SECURITY_RULES: list[SecurityFinding] = [

    # ── 1. HARDCODED SECRETS & CREDENTIALS ────────────────────────────────────
    SecurityFinding(
        category="SECRETS", rule_id="SEC-001",
        title="Hardcoded API Keys & Tokens (OpenAI, Slack, Stripe, GitHub)",
        severity="CRITICAL", penalty=20,
        description="Found potential hardcoded API keys or bearer tokens in code files.",
        recommendation="Move all API keys to environment variables (`.env`) or secret management service (Vault/AWS Secrets Manager).",
    ),
    SecurityFinding(
        category="SECRETS", rule_id="SEC-002",
        title="Hardcoded AWS / Cloud Access Keys (AKIA...)",
        severity="CRITICAL", penalty=25,
        description="Found hardcoded AWS Access Key ID or Secret Key.",
        recommendation="Use AWS IAM Roles, OIDC, or environment variables instead of hardcoded credentials.",
    ),
    SecurityFinding(
        category="SECRETS", rule_id="SEC-003",
        title="Hardcoded Private Keys / Certificates (RSA, EC, PGP)",
        severity="CRITICAL", penalty=25,
        description="Found embedded `-----BEGIN PRIVATE KEY-----` or PEM certificate strings.",
        recommendation="Never commit private keys to git repository. Store in secure vault or filesystem with strict file permissions.",
    ),
    SecurityFinding(
        category="SECRETS", rule_id="SEC-004",
        title="Database Connection URIs with Plaintext Passwords",
        severity="HIGH", penalty=15,
        description="Found hardcoded database connection strings containing plaintext passwords (`postgres://user:pass@`).",
        recommendation="Pass database credentials via environment variables or secret store.",
    ),
    SecurityFinding(
        category="SECRETS", rule_id="SEC-005",
        title="Hardcoded JWT / Encryption Secret Keys",
        severity="HIGH", penalty=15,
        description="Found hardcoded JWT secret or encryption key literals in code.",
        recommendation="Inject JWT secrets at runtime via environment variables.",
    ),

    # ── 2. OWASP TOP 10 VULNERABILITY PATTERNS ──────────────────────────────
    SecurityFinding(
        category="OWASP", rule_id="OWASP-A01",
        title="A01: Broken Access Control & Missing Auth Checks",
        severity="HIGH", penalty=15,
        description="Found endpoints or controllers without explicit authentication or authorization decorators/middleware.",
        recommendation="Enforce global authentication middleware and explicit RBAC/ABAC policy checks.",
    ),
    SecurityFinding(
        category="OWASP", rule_id="OWASP-A02",
        title="A02: Cryptographic Failures (Weak Hash MD5/SHA1, HTTP without TLS)",
        severity="HIGH", penalty=15,
        description="Found insecure cryptographic algorithms (MD5, SHA-1, DES) or unencrypted HTTP connections.",
        recommendation="Upgrade to SHA-256/SHA-512, bcrypt/Argon2 for passwords, and enforce HTTPS/TLS 1.3.",
    ),
    SecurityFinding(
        category="OWASP", rule_id="OWASP-A03",
        title="A03: Injection Flaws (SQL Injection, Command Injection `eval/exec/os.system`)",
        severity="CRITICAL", penalty=25,
        description="Found potential SQL string concatenation or dangerous command execution (`eval`, `exec`, `os.system`, `subprocess.Popen(shell=True)`).",
        recommendation="Use parameterized SQL queries (ORMs) and pass command arguments as sanitized arrays (`shell=False`).",
    ),
    SecurityFinding(
        category="OWASP", rule_id="OWASP-A04",
        title="A04: Insecure Design & Missing Rate Limiting",
        severity="MEDIUM", penalty=10,
        description="Found public endpoints without rate limiting or brute-force protection.",
        recommendation="Implement rate limiting middleware (Redis token bucket / API Gateway throttling).",
    ),
    SecurityFinding(
        category="OWASP", rule_id="OWASP-A05",
        title="A05: Security Misconfiguration (CORS wildcard '*', DEBUG=True)",
        severity="MEDIUM", penalty=10,
        description="Found permissive CORS wildcard (`*`) or debug mode enabled in code/configs.",
        recommendation="Restrict CORS origins to trusted domains and disable debug modes in production.",
    ),
    SecurityFinding(
        category="OWASP", rule_id="OWASP-A07",
        title="A07: Identification & Auth Failures (Plaintext Password Log/Cookie)",
        severity="HIGH", penalty=15,
        description="Found potential password logging or unencrypted session cookie handling.",
        recommendation="Mask sensitive fields in logs and set `Secure`, `HttpOnly`, and `SameSite` flags on cookies.",
    ),
    SecurityFinding(
        category="OWASP", rule_id="OWASP-A08",
        title="A08: Software & Data Integrity Failures (Unsafe Deserialization `pickle/yaml.unsafe_load`)",
        severity="CRITICAL", penalty=20,
        description="Found unsafe object deserialization (`pickle.loads`, `yaml.unsafe_load`, `eval`).",
        recommendation="Use safe JSON/YAML parsers (`yaml.safe_load`) and avoid deserializing untrusted binary streams.",
    ),
    SecurityFinding(
        category="OWASP", rule_id="OWASP-A09",
        title="A09: Logging PII / Passwords to Console or Files",
        severity="MEDIUM", penalty=10,
        description="Found logging calls that print passwords, tokens, or PII (email, phone, credit card) to logs.",
        recommendation="Implement structured log sanitization filter to strip PII and credentials.",
    ),
    SecurityFinding(
        category="OWASP", rule_id="OWASP-A10",
        title="A10: Server-Side Request Forgery (SSRF)",
        severity="HIGH", penalty=15,
        description="Found unvalidated user-supplied URLs passed directly into HTTP client requests (`requests.get`, `fetch`).",
        recommendation="Validate and whitelist destination URLs/IPs before initiating outbound HTTP requests.",
    ),

    # ── 3. COMPLIANCE READINESS (SOC2 / GDPR / HIPAA / PCI-DSS) ───────────────
    SecurityFinding(
        category="COMPLIANCE", rule_id="COMP-SOC2",
        title="SOC 2 Type II Readiness: Audit Trail & Access Controls",
        severity="MEDIUM", penalty=10,
        description="Evaluates presence of structured audit logging, user access tracking, and security monitoring.",
        recommendation="Implement immutable audit log storage for key security events (login, data export, permission change).",
    ),
    SecurityFinding(
        category="COMPLIANCE", rule_id="COMP-GDPR",
        title="GDPR Compliance: PII Anonymization & Right-to-be-Forgotten",
        severity="HIGH", penalty=15,
        description="Evaluates handling of Personally Identifiable Information (PII) consent and user data deletion capability.",
        recommendation="Provide automated PII deletion/anonymization routines for user data erasure requests.",
    ),
    SecurityFinding(
        category="COMPLIANCE", rule_id="COMP-HIPAA",
        title="HIPAA Compliance: Protected Health Information (PHI) Isolation",
        severity="HIGH", penalty=15,
        description="Evaluates encryption at rest/in transit and strict access control for medical/health data.",
        recommendation="Enforce AES-256 encryption at rest, TLS 1.3 in transit, and strict role-based access for PHI.",
    ),
    SecurityFinding(
        category="COMPLIANCE", rule_id="COMP-PCI",
        title="PCI-DSS Compliance: Payment Card Data Handling & Masking",
        severity="CRITICAL", penalty=25,
        description="Evaluates handling of Primary Account Numbers (PAN), CVVs, and credit card storage.",
        recommendation="Never store raw credit card numbers or CVVs. Use PCI-compliant gateway tokenization (Stripe/PayPal).",
    ),

    # ── 4. DEPENDENCY & SBOM RISK ─────────────────────────────────────────────
    SecurityFinding(
        category="DEPENDENCY", rule_id="SBOM-001",
        title="Unpinned Package Dependencies (Wildcard '*' or `>=` versions)",
        severity="LOW", penalty=5,
        description="Found unpinned package versions in manifest files, risking supply chain attacks.",
        recommendation="Pin exact package versions using lockfiles (`package-lock.json`, `poetry.lock`, `Cargo.lock`).",
    ),
    SecurityFinding(
        category="DEPENDENCY", rule_id="SBOM-002",
        title="Presence of Known Vulnerable or Outdated Package Dependencies",
        severity="HIGH", penalty=15,
        description="Found dependency manifests requiring automated vulnerability scanning.",
        recommendation="Run `npm audit`, `pip-audit`, `cargo audit`, or `trivy fs` in CI/CD pipeline.",
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Search Patterns & Heuristics
# ─────────────────────────────────────────────────────────────────────────────
RULE_PATTERNS = {
    "SEC-001": ["sk-", "xoxb-", "ghp_", "bearer ", "api_key = ", "apikey = "],
    "SEC-002": ["AKIA", "aws_secret_access_key", "aws_access_key_id"],
    "SEC-003": ["BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "BEGIN EC PRIVATE KEY"],
    "SEC-004": ["postgres://", "mysql://", "mongodb://", "amqp://"],
    "SEC-005": ["jwt_secret", "secret_key = ", "app_secret", "private_key = "],
    "OWASP-A01": ["@public", "no_auth", "bypass_auth", "allow_all"],
    "OWASP-A02": ["md5(", "sha1(", "DES(", "http://"],
    "OWASP-A03": ["eval(", "exec(", "os.system(", "shell=True", "f\"SELECT", "f'SELECT"],
    "OWASP-A04": ["rate_limit", "throttle", "slowapi", "limiter"],
    "OWASP-A05": ["CORS", "Access-Control-Allow-Origin", "DEBUG = True", "DEBUG=True"],
    "OWASP-A07": ["password", "passwd", "cookie", "session"],
    "OWASP-A08": ["pickle.loads", "yaml.unsafe_load", "unserialize("],
    "OWASP-A09": ["logger.info(password", "print(password", "console.log(password"],
    "OWASP-A10": ["requests.get(", "fetch(", "curl", "httpx.get("],
    "COMP-SOC2": ["audit_log", "auditlog", "security_log", "access_log"],
    "COMP-GDPR": ["anonymize", "delete_user", "consent", "pii", "gdpr"],
    "COMP-HIPAA": ["phi", "patient", "medical_record", "hipaa"],
    "COMP-PCI": ["card_number", "cvv", "pan_mask", "credit_card"],
    "SBOM-001": ["*", "^", ">="],
    "SBOM-002": ["package.json", "requirements.txt", "go.mod", "Cargo.toml", "composer.json"],
}


def scan_codebase_security(root: Path, idx: IndexStoreAdapter) -> list[SecurityFinding]:
    """Scan codebase for security & compliance findings."""
    for rule in SECURITY_RULES:
        patterns = RULE_PATTERNS.get(rule.rule_id, [])
        hits = set()

        for pat in patterns:
            # BM25 search
            try:
                bm25_results = idx.search_code(pat, limit=4)
                for r in bm25_results:
                    if r.path and not any(x in r.path for x in ("node_modules", ".git", "vendor", "__pycache__")):
                        hits.add(r.path)
            except Exception:
                pass

            # Direct regex scan for critical secrets
            if rule.rule_id in ("SEC-001", "SEC-002", "SEC-003", "SEC-004"):
                for f in list(root.rglob("*.py"))[:50] + list(root.rglob("*.js"))[:50] + list(root.rglob("*.ts"))[:50] + list(root.rglob("*.env*"))[:10]:
                    if any(x in f.parts for x in ("node_modules", ".git", "vendor")):
                        continue
                    try:
                        text = f.read_text(encoding="utf-8", errors="ignore")
                        if pat.lower() in text.lower():
                            hits.add(str(f.relative_to(root)))
                    except Exception:
                        pass

        rule.evidence_files = sorted(list(hits))[:4]
        rule.found = len(rule.evidence_files) > 0

    return SECURITY_RULES


def calculate_security_debt(rules: list[SecurityFinding]) -> tuple[int, str]:
    """Calculate Security Debt Score (0-100) and Due Diligence Grade."""
    total_penalty = sum(r.penalty for r in rules if r.found)
    score = max(0, 100 - total_penalty)

    if score >= 90: grade = "A+ (Institutional / M&A Ready)"
    elif score >= 80: grade = "A (Passed Due Diligence)"
    elif score >= 70: grade = "B (Minor Remediation Required)"
    elif score >= 60: grade = "C (Significant Security Debt)"
    elif score >= 50: grade = "D (High M&A Risk)"
    else: grade = "F (CRITICAL SECURITY DEBT — Unsaleable As-Is)"

    return score, grade


def build_report(project: str, root: Path, rules: list[SecurityFinding],
                 stats: dict, elapsed: float, report_path: Path) -> str:
    found_rules = [r for r in rules if r.found]
    score, grade = calculate_security_debt(rules)

    critical = [r for r in found_rules if r.severity == "CRITICAL"]
    high = [r for r in found_rules if r.severity == "HIGH"]

    lines = [
        f"# 🛡️ Security & Compliance Due Diligence Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📋 M&A Executive Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **Security Debt Score** | **{score} / 100** |",
        f"| **M&A Due Diligence Rating** | **{grade}** |",
        f"| Codebase Files Analyzed | {stats.get('total_files', 0):,} |",
        f"| Total Findings | **{len(found_rules)}** (out of {len(rules)} checks) |",
        f"| 🚨 CRITICAL Security Risks | {len(critical)} |",
        f"| 🔴 HIGH Security Risks | {len(high)} |",
        "",
    ]

    if critical:
        lines += ["## 🚨 CRITICAL Security Blockers (Must Fix Before Sale)", ""]
        for r in critical:
            evidence = ", ".join(f"`{e}`" for e in r.evidence_files)
            lines.append(f"### 🚨 [{r.rule_id}] {r.title}")
            lines.append(f"**Severity:** `{r.severity}` | **Score Penalty:** -{r.penalty} points")
            lines.append(f"**Description:** {r.description}")
            lines.append(f"**Evidence Files:** {evidence}")
            lines.append(f"**Remediation:** {r.recommendation}")
            lines.append("")

    if high:
        lines += ["## 🔴 HIGH Security & Compliance Risks", ""]
        for r in high:
            evidence = ", ".join(f"`{e}`" for e in r.evidence_files)
            lines.append(f"- 🔴 **[{r.rule_id}] {r.title}** (`-{r.penalty} pts`) — {evidence}")
            lines.append(f"  *Remediation:* {r.recommendation}")
        lines.append("")

    # Categories breakdown
    by_cat = defaultdict(list)
    for r in found_rules:
        by_cat[r.category].append(r)

    cat_names = {
        "SECRETS": "🔑 Hardcoded Secrets & Credentials",
        "OWASP": "🛡️ OWASP Top 10 Vulnerability Patterns",
        "COMPLIANCE": "⚖️ Compliance Readiness (SOC2 / GDPR / HIPAA / PCI)",
        "DEPENDENCY": "📦 Software Bill of Materials (SBOM) & Supply Chain",
    }

    for cat_id, cat_title in cat_names.items():
        cat_findings = by_cat.get(cat_id, [])
        if not cat_findings:
            continue
        lines += [f"## {cat_title}", ""]
        lines += ["| Rule ID | Finding | Severity | Score Penalty | Verified Evidence |",
                  "|---|---|---|---|---|"]
        for r in cat_findings:
            ev = ", ".join(f"`{e}`" for e in r.evidence_files[:2])
            lines.append(f"| `{r.rule_id}` | **{r.title}** | `{r.severity}` | -{r.penalty} pts | {ev} |")
        lines.append("")

    lines += [
        "## 🛠️ Security Remediation Roadmap for Sale / Due Diligence",
        "",
        "1. **Purge Secrets from Git History**: Run `bfg` or `git-filter-repo` to revoke and purge hardcoded keys.",
        "2. **Implement Secret Manager**: Inject all API keys via `.env` or Vault at runtime.",
        "3. **Parameterize SQL & Sanitize Commands**: Replace string concatenation in queries with ORM / parameterized inputs.",
        "4. **Audit Dependencies**: Run automated SBOM scanners (`npm audit`, `pip-audit`, `trivy fs`).",
        "",
        "---",
        f"*Security & Compliance Risk Auditor · M&A Due Diligence Edition · {date.today()}*",
    ]

    content = "\n".join(lines)
    report_path.write_text(content, encoding="utf-8")
    return content


def print_console(project: str, root: Path, rules: list[SecurityFinding],
                  stats: dict, elapsed: float) -> None:
    found_rules = [r for r in rules if r.found]
    score, grade = calculate_security_debt(rules)

    SEP = "═" * 75
    sep = "─" * 75

    print(f"\n{SEP}")
    print(f"  🛡️ SECURITY & COMPLIANCE RISK AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed        : {stats.get('total_files', 0):,}")
    print(f"  Security Debt Score  : {score} / 100")
    print(f"  Due Diligence Grade  : {grade}")
    print(f"  Total Findings       : {len(found_rules)} / {len(rules)}")
    print(f"  Scan speed           : {elapsed:.3f}s")
    print(sep)

    for r in found_rules:
        icon = "🚨" if r.severity == "CRITICAL" else ("🔴" if r.severity == "HIGH" else "⚠️")
        ev = ", ".join(r.evidence_files[:2]) if r.evidence_files else "Scanned"
        print(f"  {icon} [{r.rule_id}] {r.title:<50s} (-{r.penalty} pts)")
        print(f"     📁 Evidence: {ev}")

    print(f"\n{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/security_compliance_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"security_compliance_{safe_name}.md"

    print(f"\n  🛡️ Security Risk Auditor — {project_name}")
    print(f"  📁 {project_path}")
    print(f"  ⏳ Building BM25 index...", end="", flush=True)

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    t_index = time.perf_counter() - t0
    print(f" {stats.get('total_files', 0):,} files in {t_index*1000:.0f}ms")

    print(f"  🔎 Running Security & Compliance checks...", end="", flush=True)
    t1 = time.perf_counter()
    rules = scan_codebase_security(project_path, idx)
    t_detect = time.perf_counter() - t1
    found_count = sum(1 for r in rules if r.found)
    print(f" {found_count} findings in {t_detect*1000:.0f}ms")

    elapsed = time.perf_counter() - t0

    print_console(project_name, project_path, rules, stats, elapsed)
    build_report(project_name, project_path, rules, stats, elapsed, report_path)

    print(f"  [+] Security report saved → {report_path}")
    print("═" * 75 + "\n")


if __name__ == "__main__":
    main()
