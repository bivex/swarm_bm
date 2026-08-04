#!/usr/bin/env python3
"""
Register swarm-auditors-mcp tool schemas into ~/.gemini/antigravity-cli/mcp/swarm-auditors-mcp/
"""
import json
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.infrastructure.mcp_server_adapter import create_swarm_mcp_server

def main():
    mcp = create_swarm_mcp_server(root_path=root_dir)
    target_dir = Path.home() / ".gemini" / "antigravity-cli" / "mcp" / "swarm-auditors-mcp"
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"[+] Exporting tool schemas to {target_dir}")

    # Inspect FastMCP tools
    tools = mcp._tool_manager.list_tools()
    for tool in tools:
        tool_name = tool.name
        schema = {
            "name": tool_name,
            "description": tool.description or "",
            "parameters": tool.parameters if hasattr(tool, "parameters") and tool.parameters else {
                "type": "object",
                "properties": {}
            }
        }
        
        # If parameters is pydantic model schema or dict
        if hasattr(tool.parameters, "model_dump"):
            schema["parameters"] = tool.parameters.model_dump(exclude_none=True)
        elif isinstance(tool.parameters, dict):
            schema["parameters"] = tool.parameters

        out_file = target_dir / f"{tool_name}.json"
        out_file.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  ✅ Wrote {out_file.name}")

    print(f"\n[+] Total {len(tools)} MCP tools registered in {target_dir}")

if __name__ == "__main__":
    main()
