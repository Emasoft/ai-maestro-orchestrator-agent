#!/usr/bin/env python3
"""
Universal Server Orchestration for Tests

A test fixture helper that orchestrates multi-server startup for integration testing.
Works with ANY server combination: frontend dev servers, API backends, databases, etc.

Features:
- Start multiple servers in parallel
- Wait for port readiness (configurable timeout)
- Execute test command after all servers ready
- Graceful cleanup via SIGTERM then SIGKILL
- Returns test exit code for CI integration

Example usage:
    # Single server
    python with_server.py --server "npm run dev" --port 3000 -- pytest tests/

    # Multiple servers (frontend + backend)
    python with_server.py \
        --server "npm run dev" --port 5173 \
        --server "python api.py" --port 8000 \
        -- pytest tests/integration/

    # With timeout
    python with_server.py --server "npm run dev" --port 3000 --timeout 60 -- npm test

Part of EOA (Emasoft Orchestrator Agent) verification-patterns skill.
"""

# WHY: Future annotations for forward reference compatibility in type hints
from __future__ import annotations

import subprocess
import socket
import time
import sys
import argparse


def verify_config(servers: list[str], ports: list[int], command: list[str]) -> bool:
    """Verify configuration is valid before execution.

    WHY: Fail-fast validation catches configuration errors before starting any
    servers, preventing partial startup states that are harder to clean up.
    """
    if not servers:
        print("Error: No servers specified")
        return False
    if not ports:
        print("Error: No ports specified")
        return False
    if len(servers) != len(ports):
        print(f"Error: Server count ({len(servers)}) != port count ({len(ports)})")
        return False
    if not command:
        print("Error: No command specified")
        return False
    # WHY: Validate ports are in valid range to catch typos early
    for port in ports:
        if not (1 <= port <= 65535):
            print(f"Error: Invalid port {port} (must be 1-65535)")
            return False
    return True


def verify_server_stopped(process: subprocess.Popen, server_index: int) -> bool:
    """Verify a server process has actually stopped.

    WHY: Confirms cleanup was successful - prevents orphaned server processes
    that could cause port conflicts in subsequent test runs.
    """
    poll_result = process.poll()
    if poll_result is None:
        print(f"Warning: Server {server_index} still running after stop attempt")
        return False
    print(f"Server {server_index} confirmed stopped (exit code: {poll_result})")
    return True


def is_server_ready(port: int, timeout: int = 30) -> bool:
    """Wait for server to be ready by polling the port."""
    # WHY: Polling with socket connection is the most reliable cross-platform
    # method to detect server readiness - works for any TCP server
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # WHY: 1-second connection timeout prevents hanging on unresponsive ports
            with socket.create_connection(("localhost", port), timeout=1):
                return True
        except (socket.error, ConnectionRefusedError):
            # WHY: 0.5s sleep balances responsiveness vs CPU usage during polling
            time.sleep(0.5)
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Run command with one or more servers")
    parser.add_argument(
        "--server",
        action="append",
        dest="servers",
        required=True,
        help="Server command (can be repeated)",
    )
    parser.add_argument(
        "--port",
        action="append",
        dest="ports",
        type=int,
        required=True,
        help="Port for each server (must match --server count)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds per server (default: 30)",
    )
    parser.add_argument(
        "command", nargs=argparse.REMAINDER, help="Command to run after server(s) ready"
    )

    args = parser.parse_args()

    # Remove the '--' separator if present
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]

    # WHY: Fail-fast validation before starting any servers
    if not verify_config(args.servers or [], args.ports or [], args.command):
        sys.exit(1)

    servers = []
    for cmd, port in zip(args.servers, args.ports):
        servers.append({"cmd": cmd, "port": port})

    server_processes = []

    try:
        # Start all servers
        for i, server in enumerate(servers):
            print(f"Starting server {i + 1}/{len(servers)}: {server['cmd']}")

            # WHY: shell=True is required to support compound commands with cd, &&, pipes
            # which are common in dev server startup scripts (e.g., "cd app && npm run dev")
            process = subprocess.Popen(
                server["cmd"],
                shell=True,
                # WHY: Capture stdout/stderr to prevent server output from polluting test output
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            server_processes.append(process)

            # Wait for this server to be ready
            print(f"Waiting for server on port {server['port']}...")
            if not is_server_ready(server["port"], timeout=args.timeout):
                raise RuntimeError(
                    f"Server failed to start on port {server['port']} within {args.timeout}s"
                )

            print(f"Server ready on port {server['port']}")

        print(f"\nAll {len(servers)} server(s) ready")

        # WHY: Run test command and propagate its exit code for CI integration
        print(f"Running: {' '.join(args.command)}\n")
        result = subprocess.run(args.command)
        # WHY: Propagate test exit code (not hardcoded 0) so CI pipelines can detect failures
        sys.exit(result.returncode)

    finally:
        # WHY: Cleanup in finally block ensures servers are stopped even on exceptions/interrupts
        print(f"\nStopping {len(server_processes)} server(s)...")
        all_stopped = True
        for i, process in enumerate(server_processes):
            try:
                # WHY: SIGTERM first allows graceful shutdown (save state, close connections)
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # WHY: SIGKILL as fallback for unresponsive processes prevents orphaned servers
                process.kill()
                process.wait()
            # WHY: Verify each server actually stopped to prevent orphaned processes
            if not verify_server_stopped(process, i + 1):
                all_stopped = False
        if all_stopped:
            print("All servers verified stopped")
        else:
            print("Warning: Some servers may not have stopped cleanly")


if __name__ == "__main__":
    main()
