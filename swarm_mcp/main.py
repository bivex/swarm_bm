import sys
from pathlib import Path

# Add root directory to sys.path
root_dir = Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from swarm_mcp.infrastructure.mcp_server_adapter import create_swarm_mcp_server


def main() -> None:
    server = create_swarm_mcp_server(root_path=root_dir)
    print(f"[+] Launching Swarm Hexagonal MCP Server for root: {root_dir}")
    server.run()


if __name__ == "__main__":
    main()
