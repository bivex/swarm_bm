import json
import time
from pathlib import Path

from swarm_mcp.application.senior_audit import SeniorCodebaseAuditEngine
from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter
from swarm_mcp.infrastructure.job_engine_adapter import JobEngineAdapter


def run_audit(repo_path: str, label: str) -> dict:
    root = Path(repo_path)
    engine = SeniorCodebaseAuditEngine(IndexStoreAdapter(), JobEngineAdapter())
    data = engine.run_10_agent_senior_audit(root)

    lines = [
        f"# 🏛️ Senior Architect Audit: {label}",
        f"",
        f"| Параметр | Значение |",
        f"|----------|---------|",
        f"| Путь | `{data['root_path']}` |",
        f"| Файлов в индексе | {data['total_files']} |",
        f"| Символов в AST | {data['total_symbols']} |",
        f"| Задано вопросов | {data['total_questions_audited']} |",
        f"| Вопросов с находками | {data['questions_with_real_findings']} |",
        f"| Время аудита | {data['elapsed_seconds']} с |",
        f"",
        f"---",
        f"",
    ]

    for domain_res in data["domain_results"]:
        if not domain_res["findings"]:
            continue  # domain was completely dark — skip
        lines.append(f"## 🤖 {domain_res['domain']} — {domain_res['agent_id']}")
        lines.append(f"_Вопросов с находками: {domain_res['questions_with_findings']}_")
        lines.append("")
        for f in domain_res["findings"]:
            lines.append(f"### ❓ {f['question']}")

            if f["matched_files"]:
                lines.append("**📁 Файлы (BM25 top-6 по релевантности):**")
                for fp in f["matched_files"]:
                    lines.append(f"- `{fp}`")

            if f["symbols"]:
                lines.append("")
                lines.append("**🔬 AST Символы:**")
                lines.append("| Имя | Тип | Файл | Строка |")
                lines.append("|-----|-----|------|--------|")
                for s in f["symbols"]:
                    name = s.get("name", "")
                    kind = s.get("kind", "")
                    path = s.get("path", "")
                    line = s.get("line", 0)
                    lines.append(f"| `{name}` | {kind} | `{path}` | {line} |")

            lines.append("")

    report = "\n".join(lines)
    artifact_path = Path(
        "/Users/password9090/.gemini/antigravity-cli/brain/b1a8b172-4960-462a-bad1-43d8b7e774ad"
    ) / f"{label.replace(' ', '_').lower()}_senior_audit_report.md"
    artifact_path.write_text(report, encoding="utf-8")
    print(f"[+] Report written → {artifact_path}")
    return data


if __name__ == "__main__":
    import sys
    repo = sys.argv[1] if len(sys.argv) > 1 else "/tmp/django_senior_audit"
    label = sys.argv[2] if len(sys.argv) > 2 else "Django"
    data = run_audit(repo, label)
    print(json.dumps({
        "total_files": data["total_files"],
        "questions_with_findings": data["questions_with_real_findings"],
        "elapsed_seconds": data["elapsed_seconds"],
    }, indent=2))
