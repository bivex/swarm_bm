---
name: revenue-stack-auditor
description: Performs zero-magic BM25+AST revenue maximization audits and technology stack slicing on any codebase to find monetization points, proprietary swap targets, and license risks.
---

# 💎 Revenue & Technology Stack Auditor Skill

Use this skill when auditing any repository for **monetization potential**, **technology stack breakdown**, **license compliance**, or **M&A/SaaS product extraction**.

## 🛠️ Available Auditors

All auditors use **zero-magic BM25 + AST evidence scanning** (no LLM hallucinated assumptions, only factual code hits).

### 1. Revenue Maximization Auditor (11 Blocks)
- **Location**: `scratch/auditors/revenue_audit.py`
- **Purpose**: Identifies where the client already gets value, where to embed commercial paywalls, subscription cost drivers, and ARR forecasts.
- **Run command**:
  ```bash
  PYTHONPATH=bm25_server_FS_for-AI-asking:. python3 scratch/auditors/revenue_audit.py /path/to/project [ProjectName]
  ```

### 2. Technology Stack Slicer (60+ Techs, 12 Categories)
- **Location**: `scratch/auditors/stack_slicer.py`
- **Purpose**: Slices the technology stack, checks component licenses (GPL/AGPL/BSL/SSPL/MIT), and scores replaceability with proprietary alternatives.
- **Run command**:
  ```bash
  PYTHONPATH=bm25_server_FS_for-AI-asking:. python3 scratch/auditors/stack_slicer.py /path/to/project [ProjectName]
  ```

---

## 📊 11 Revenue Strategy Specialist Blocks

1. **Irina Volkov** (Core Value Monetization) — Critical business functions, output generators
2. **Marcus Billing** (Volume-Based Billing) — Per-user, per-request, per-file counters
3. **Victoria Enterprise** (Enterprise Sales Surface) — RBAC, SSO, multi-tenant isolation, audit logs
4. **Stefan Modular** (Standalone & SaaS Extraction) — Freemium vs Premium split
5. **Gennady Cost-Cutter** (ROI Proof & Savings) — Automation value, manual cost savings
6. **Boris Retention** (LTV & Stickiness) — Data gravity, lock-in, churn prevention
7. **Pavel Services** (Professional Services) — SLA, custom reporting, complex migration
8. **Upsell Ulrika** (ARPU Expansion) — Priority queues, GPU/Fast tier, developer API
9. **Recurring Riccardo** (MRR Infrastructure) — CPU/GPU, storage growth, always-on processes
10. **Ivan Monetizer** (Potential Scorer & ARR) — Multi-tier ARR forecast ($10k–$500k+)
11. **Legal Lars** (License Risk Scanner) — Factual scan of `LICENSE*`, SPDX headers, dependencies

---

## ⚖️ License Risk Levels

| Level | Risk | Action |
|---|---|---|
| **0/5** | ✅ Permissive (MIT, Apache-2.0, BSD) | Free commercial use |
| **1/5** | ⚠️ Weak Copyleft (MPL-2.0, LGPL-2.1/3.0, EULA) | Require vendor terms or dynamic linking |
| **2/5** | ⚠️ Freemium / Weak Copyleft | Pay for commercial license |
| **3/5** | 🟠 Source Available (BSL-1.1, CC-BY-SA) | Legal consultation required before SaaS |
| **4/5** | 🔴 Strong Copyleft (GPL-2.0/3.0, SSPL-1.0) | Copyleft linkage obligation |
| **5/5** | 🚨 Network Copyleft (AGPL-3.0, CC-BY-NC) | Blocks SaaS embedding without commercial agreement |

---

## 🔄 Proprietary Swap Strategy

For open-source projects with copyleft or vendor lock-in risks:
- **AGPL/GPL Modules**: Replace with out-of-process REST/gRPC microservices.
- **Leaky Buckets / Rate Limiters**: Replace with proprietary Redis/SaaS billing limiters.
- **Media / SIP Stack**: Build proprietary C/Go dynamic `.so` plugins (MPL-1.1 compliant).
