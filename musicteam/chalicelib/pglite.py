"""Core PGlite process management.

This file is derived from py-pglite, found at
https://github.com/wey-gu/py-pglite/blob/6f27fd3567456bcc2c96428c2ff3ca72b7be70b3/src/py_pglite/manager.py
retrieved on January 21, 2026.

Licensed according to the Apache License, version 2.0.

"""

import json
import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path
from textwrap import dedent
from typing import Any

import psutil


class PGliteManager:
    """Manages PGlite process lifecycle for testing.

    Framework-agnostic PGlite process manager. Provides database connections
    through framework-specific methods that require their respective dependencies.
    """

    EXTENSIONS = {
        "uuid_ossp": {
            "module": "@electric-sql/pglite/contrib/uuid_ossp",
            "name": "uuid_ossp",
        }
    }

    def __init__(self, work_dir: str | Path | None = None):
        """Initialize PGlite manager."""

        if isinstance(work_dir, str):
            work_dir = Path(work_dir)

        self.process: subprocess.Popen[str] | None = None
        self.socket_path = self._get_secure_socket_path()
        self.work_dir = self._setup_work_dir(work_dir)
        self._original_cwd: str | None = None
        self._shared_engine: Any | None = None

        # Set up logging
        self.logger = logging.getLogger(__name__)

    def __enter__(self) -> "PGliteManager":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.stop()

    def _get_secure_socket_path(self) -> Path:
        base_dir = Path(tempfile.mkdtemp(prefix="pglite-socket-"))
        return base_dir / ".s.PGSQL.5432"

    def _setup_work_dir(self, work_dir: Path | None) -> Path:
        """Setup working directory for PGlite files."""
        if not work_dir:
            work_dir = Path(tempfile.mkdtemp(prefix="pglite-"))

        # Create package.json if it doesn't exist
        package_json = work_dir / "package.json"
        if not package_json.exists():
            package_content = {
                "name": "py-pglite-env",
                "version": "1.0.0",
                "description": "PGlite test environment for py-pglite",
                "scripts": {"start": "node pglite_manager.js"},
                "dependencies": {
                    "@electric-sql/pglite": "^0.3.15",
                    "@electric-sql/pglite-socket": "^0.0.20",
                },
            }
            with open(package_json, "w") as f:
                json.dump(package_content, f, indent=2)

        # Create pglite_manager.js
        manager_js = work_dir / "pglite_manager.js"

        ext_requires = []
        ext_configs = []
        for ext_name, ext_info in self.EXTENSIONS.items():
            ext_requires.append(
                f"const {{ {ext_info['name']} }} = require('{ext_info['module']}');"
            )
            ext_configs.append(f"    {ext_name}: {ext_info['name']}")

        ext_requires_str = "\n".join(ext_requires)
        ext_configs_str = ",\n".join(ext_configs)
        extensions_obj_str = f"{{\n{ext_configs_str}\n}}" if ext_configs else "{}"

        # Generate JavaScript content based on socket mode
        js_content = self._generate_unix_js_content(
            ext_requires_str, extensions_obj_str
        )
        with open(manager_js, "w") as f:
            f.write(js_content)

        return work_dir

    def _generate_unix_js_content(
        self, ext_requires_str: str, extensions_obj_str: str
    ) -> str:
        """Generate JavaScript content for Unix socket mode (original logic)."""
        return dedent(f"""
            const {{ PGlite }} = require('@electric-sql/pglite');
            const {{ PGLiteSocketServer }} = require('@electric-sql/pglite-socket');
            const fs = require('fs');
            const path = require('path');
            const {{ unlink }} = require('fs/promises');
            const {{ existsSync }} = require('fs');
            {ext_requires_str}

            const SOCKET_PATH = '{self.socket_path}';

            async function cleanup() {{
                if (existsSync(SOCKET_PATH)) {{
                    try {{
                        await unlink(SOCKET_PATH);
                        console.log(`Removed old socket at ${{SOCKET_PATH}}`);
                    }} catch (err) {{
                        // Ignore errors during cleanup
                    }}
                }}
            }}

            async function startServer() {{
                try {{
                    // Create a PGlite instance with extensions
                    const db = new PGlite('./datadir', {{
                        extensions: {extensions_obj_str}
                    }});

                    // Clean up any existing socket
                    await cleanup();

                    // Create and start a socket server
                    const server = new PGLiteSocketServer({{
                        db,
                        path: SOCKET_PATH,
                    }});
                    await server.start();
                    console.log(`Server started on socket ${{SOCKET_PATH}}`);

                    // Handle graceful shutdown
                    process.on('SIGINT', async () => {{
                        console.log('Received SIGINT, shutting down gracefully...');
                        try {{
                            await server.stop();
                            await db.close();
                            console.log('Server stopped and database closed');
                        }} catch (err) {{
                            console.error('Error during shutdown:', err);
                        }}
                        process.exit(0);
                    }});

                    process.on('SIGTERM', async () => {{
                        console.log('Received SIGTERM, shutting down gracefully...');
                        try {{
                            await server.stop();
                            await db.close();
                            console.log('Server stopped and database closed');
                        }} catch (err) {{
                            console.error('Error during shutdown:', err);
                        }}
                        process.exit(0);
                    }});

                    // Keep the process alive
                    process.on('exit', () => {{
                        console.log('Process exiting...');
                    }});

                }} catch (err) {{
                    console.error('Failed to start PGlite server:', err);
                    process.exit(1);
                }}
            }}

            startServer();
        """).strip()

    def _cleanup_socket(self) -> None:
        """Clean up the PGlite socket file."""
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
                self.logger.info(f"Cleaned up socket at {self.socket_path}")
            except Exception as e:
                self.logger.warning(f"Failed to clean up socket: {e}")

    def _kill_existing_processes(self) -> None:
        """Kill any existing PGlite processes that might conflict with this socket."""
        try:
            if self.work_dir:
                my_target_dir = str(self.work_dir)

            for proc in psutil.process_iter(["pid", "name", "cmdline", "cwd"]):
                if proc.info["cmdline"] and any(
                    "pglite_manager.js" in cmd for cmd in proc.info["cmdline"]
                ):
                    # Use exact directory match to avoid killing
                    # processes in similar paths
                    try:
                        proc_cwd = proc.info.get("cwd", "")
                        if proc_cwd == my_target_dir:
                            pid = proc.info["pid"]
                            self.logger.info(f"Killing existing PGlite process: {pid}")
                            proc.kill()
                            proc.wait(timeout=5)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        # Process already gone or can't access it
                        continue
        except Exception as e:
            self.logger.warning(f"Error killing existing PGlite processes: {e}")

    def _kill_all_pglite_processes(self) -> None:
        """Kill all PGlite processes globally (more aggressive cleanup
        for termination).
        """
        try:
            killed_processes = []
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                if proc.info["cmdline"] and any(
                    "pglite_manager.js" in cmd for cmd in proc.info["cmdline"]
                ):
                    try:
                        pid = proc.info["pid"]
                        self.logger.info(f"Killing PGlite process globally: {pid}")
                        proc.kill()
                        proc.wait(timeout=5)
                        killed_processes.append(pid)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        # Process already gone or can't access it
                        continue

            if killed_processes:
                self.logger.info(
                    f"Killed {len(killed_processes)} "
                    f"PGlite processes: {killed_processes}"
                )
        except Exception as e:
            self.logger.warning(f"Error killing all PGlite processes: {e}")

    def _install_dependencies(self, work_dir: Path) -> None:
        """Install npm dependencies if needed."""
        node_modules = work_dir / "node_modules"
        if not node_modules.exists():
            self.logger.info("Installing npm dependencies...")
            result = subprocess.run(
                ["npm", "install"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                check=True,
                timeout=60,  # Add timeout for npm install
            )
            self.logger.info(f"npm install completed: {result.stdout}")

    def start(self) -> None:
        """Start the PGlite server."""
        if self.process is not None:
            self.logger.warning("PGlite process already running")
            return

        # Setup
        self._kill_existing_processes()
        self._cleanup_socket()

        self._original_cwd = os.getcwd()
        os.chdir(self.work_dir)

        try:
            # Install dependencies
            self._install_dependencies(self.work_dir)

            # Prepare environment for Node.js process
            env = os.environ.copy()

            # Ensure Node.js can find the required modules
            env["NODE_PATH"] = str(self.work_dir)
            self.logger.info(f"Setting NODE_PATH to: {self.work_dir}")

            # Start PGlite process with limited output buffering
            self.logger.info("Starting PGlite server...")
            self.process = subprocess.Popen(
                ["node", "pglite_manager.js"],
                env=env,
                text=True,
                preexec_fn=(
                    os.setsid if hasattr(os, "setsid") else None
                ),  # Create new process group on Unix
            )

            # Wait for startup with robust monitoring
            start_time = time.time()
            ready_logged = False

            while time.time() - start_time < 30:
                # Check if process died
                if self.process.poll() is not None:
                    raise RuntimeError("PGlite process died during startup")

                # Unix socket readiness check
                if self.socket_path.exists() and not ready_logged:
                    self.logger.info("PGlite socket created, server should be ready...")
                    ready_logged = True

                    # Test basic connectivity to ensure it's really ready
                    try:
                        import socket

                        test_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        test_socket.settimeout(1)
                        test_socket.connect(str(self.socket_path))
                        test_socket.close()
                        self.logger.info("PGlite server started successfully")
                        break
                    except (ImportError, OSError):
                        # Socket exists but not ready yet, continue waiting
                        pass

                time.sleep(0.5)  # Check more frequently for better responsiveness
            else:
                # Timeout - cleanup and raise error
                if self.process and self.process.poll() is None:
                    self.logger.warning("PGlite server startup timeout, terminating...")
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.logger.warning("Force killing PGlite process...")
                        self.process.kill()
                        self.process.wait()

                raise RuntimeError("PGlite server failed to start within 30 seconds")

        finally:
            # Restore working directory
            if self._original_cwd:
                os.chdir(self._original_cwd)

    def stop(self) -> None:
        """Stop the PGlite server."""
        if self.process is None:
            return

        try:
            # Send SIGTERM first for graceful shutdown
            self.logger.debug("Sending SIGTERM to PGlite process...")

            # Try to terminate the entire process group if it exists
            if hasattr(os, "killpg") and hasattr(self.process, "pid"):
                try:
                    # Try to kill the process group first (includes child processes)
                    os.killpg(os.getpgid(self.process.pid), 15)  # SIGTERM
                    self.logger.debug("Sent SIGTERM to process group")
                except (OSError, ProcessLookupError):
                    # Fall back to single process termination
                    self.process.terminate()
            else:
                self.process.terminate()

            # Wait for graceful shutdown with timeout
            try:
                self.process.wait(timeout=5)
                self.logger.info("PGlite server stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                self.logger.warning(
                    "PGlite process didn't stop gracefully, force killing..."
                )

                # Try to kill the entire process group first
                if hasattr(os, "killpg") and hasattr(self.process, "pid"):
                    try:
                        os.killpg(os.getpgid(self.process.pid), 9)  # SIGKILL
                        self.logger.debug("Sent SIGKILL to process group")
                    except (OSError, ProcessLookupError):
                        # Fall back to single process kill
                        self.process.kill()
                else:
                    self.process.kill()

                try:
                    self.process.wait(timeout=2)
                    self.logger.info("PGlite server stopped forcefully")
                except subprocess.TimeoutExpired:
                    self.logger.error("Failed to kill PGlite process!")
                    # Use global cleanup as last resort when normal termination fails
                    self._kill_all_pglite_processes()

        except Exception as e:
            self.logger.warning(f"Error stopping PGlite: {e}")
        finally:
            self.process = None
            # Additional cleanup: kill any remaining pglite processes
            # Note: Global cleanup is only used in error conditions, not normal stop
            self._cleanup_socket()

    def is_running(self) -> bool:
        """Check if PGlite process is running."""
        return self.process is not None and self.process.poll() is None

    def restart(self) -> None:
        """Restart the PGlite server.

        Stops the current server if running and starts a new one.
        """
        if self.is_running():
            self.stop()
        self.start()

    def get_connection_string(self) -> str:
        """Get the database connection string for framework-agnostic usage.

        Returns:
            PostgreSQL connection string

        Raises:
            RuntimeError: If PGlite server is not running
        """
        if not self.is_running():
            raise RuntimeError("PGlite server is not running. Call start() first.")

        socket_dir = self.socket_path.parent

        return f"postgresql+psycopg://postgres:postgres@/postgres?host={socket_dir}"

    def get_dsn(self) -> str:
        """Get the database DSN string for framework-agnostic usage.

        Returns:
            PostgreSQL DSN string
        """
        if not self.is_running():
            raise RuntimeError("PGlite server is not running. Call start() first.")

        socket_dir = self.socket_path.parent

        return f"host={socket_dir} dbname=postgres user=postgres password=postgres"

    def get_psycopg_uri(self) -> str:
        """Get the database URI for psycopg usage.

        Returns:
            PostgreSQL URI string compatible with psycopg

        Raises:
            RuntimeError: If PGlite server is not running
        """
        if not self.is_running():
            raise RuntimeError("PGlite server is not running. Call start() first.")

        socket_dir = self.socket_path.parent

        return f"postgresql://postgres:postgres@/postgres?host={socket_dir}"
