# ⚠️ SwarmBM — ISO/IEC 23894:2023 AI Risk Management Plan

> **Scope**: ISO/IEC 23894:2023 / ISO 31000 AI Risk Governance Framework

---

## 1. AI Risk Context & Criteria
SwarmBM operates an AI Agent Swarm and Codebase Intelligence System. Risk appetite and criteria are defined to prevent LLM hallucinations, data poisoning, and unhandled exceptions.

## 2. AI Risk Identification & Register
| Risk ID | Source | Consequence | Likelihood | Mitigation / Risk Treatment |
|---|---|---|---|---|
| **AIR-001** | LLM Hallucinations in Code Analysis | Incorrect symbol mapping | Low | AST-grounded validation (BM25 + AST parsers) |
| **AIR-002** | Prompt Injection & Malicious Inputs | Escalation or unauthorized actions | Medium | Strict Prompt Sanitization Guardrails |
| **AIR-003** | Data Drift / Concept Drift | Reduced scan accuracy on new syntax | Low | Periodic benchmark evaluation and update of AST parsers |
| **AIR-004** | Resource Exhaustion (Token Overrun) | Budget overrun on API calls | Low | Token budgeting caps & local model fallback |

## 3. Human Oversight & Deactivation
- **Human-in-the-Loop**: High-risk actions require explicit user approval.
- **Circuit Breaker**: Instant deactivation & graceful fallback mechanisms built into task handlers.
