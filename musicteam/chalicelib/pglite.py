"""Core PGlite process management.

This file is derived from py-pglite, found at
https://github.com/wey-gu/py-pglite/blob/6f27fd3567456bcc2c96428c2ff3ca72b7be70b3/src/py_pglite/manager.py
retrieved on January 21, 2026.

Licensed according to the Apache License, version 2.0.

"""

import hashlib
import json
import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any


class PGliteManager:
    """Manages PGlite process lifecycle for testing.

    Framework-agnostic PGlite process manager. Provides database connections
    through framework-specific methods that require their respective dependencies.
    """

    DEPENDENCIES = {
        "@electric-sql/pglite": "0.5.8",
        "@electric-sql/pglite-socket": "0.2.11",
        "@electric-sql/pglite-pgvector": "0.0.9",
    }

    EXTENSIONS = ["uuid_ossp", "@electric-sql/pglite-pgvector:vector"]

    def __init__(self, work_dir: str | Path | None = None):
        """Initialize PGlite manager."""

        if isinstance(work_dir, str):
            work_dir = Path(work_dir).resolve()

        self.process: subprocess.Popen[str] | None = None
        self.work_dir = self._setup_work_dir(work_dir)
        if work_dir:
            assert isinstance(self.work_dir, Path)  # type narrowing
            self.socket_path = None
            self.ready_flag = self.work_dir / "server-ready"
        else:
            self.socket_path = self._get_secure_socket_path()
            self.ready_flag = self.socket_path.parent / "server-ready"

        # Set up logging
        self.logger = logging.getLogger(__name__)

    def __enter__(self) -> "PGliteManager":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.stop()

    def _install_pglite(self) -> Path:
        # Base dir will be the user's cache folder plus a hash of the dependencies
        pglite_dir = os.path.expanduser("~/.cache/pglite")
        dephash = hashlib.sha256(json.dumps(self.DEPENDENCIES).encode()).hexdigest()[
            :15
        ]
        pglite_ver_dir = Path(pglite_dir) / dephash
        pglite_ver_dir.mkdir(parents=True, exist_ok=True)

        # Create package.json if it doesn't exist
        package_json = pglite_ver_dir / "package.json"
        if package_json.exists():
            return pglite_ver_dir

        extensions = ",".join(self.EXTENSIONS)
        package_content = {
            "name": "py-pglite-env",
            "version": "1.0.0",
            "description": "PGlite test environment for py-pglite",
            "scripts": {"db": f"pglite-server -m 8 --extensions={extensions}"},
            "dependencies": self.DEPENDENCIES,
        }
        with open(package_json, "w") as f:
            json.dump(package_content, f, indent=2)

        # npm install
        self.logger.info("Installing npm dependencies...")
        subprocess.run(["npm", "install"], cwd=pglite_ver_dir, check=True)

        return pglite_ver_dir

    def _get_secure_socket_path(self) -> Path:
        base_dir = Path(tempfile.mkdtemp(prefix="pglite-socket-"))
        return base_dir / ".s.PGSQL.5432"

    def _setup_work_dir(self, work_dir: Path | None) -> Path | str:
        """Setup working directory for PGlite files."""
        if work_dir is None:
            return "memory://"

        work_dir = work_dir / "datadir"
        work_dir.mkdir(parents=True, exist_ok=True)
        return work_dir

    def start(self) -> None:
        """Start the PGlite server."""
        if self.process is not None:
            self.logger.warning("PGlite process already running")
            return

        if (self.socket_path and self.socket_path.exists()) or self.ready_flag.exists():
            self.logger.warning(
                "Found existing socket -- PGlite may already be running"
            )
            return

        # Install dependencies
        self.app_dir = self._install_pglite()

        # Reset the ready flag
        self.ready_flag.unlink(missing_ok=True)

        # Start PGlite process with limited output buffering
        self.logger.info("Starting PGlite server...")
        self.process = subprocess.Popen(
            [
                "npm",
                "run",
                "db",
                "--",
                f"--db={self.work_dir}",
                f"--run=touch {self.ready_flag}",
            ]
            + ([f"--path={self.socket_path}"] if self.socket_path else []),
            cwd=self.app_dir,
            text=True,
            preexec_fn=(
                os.setsid if hasattr(os, "setsid") else None
            ),  # Create new process group on Unix
        )

        # Wait for startup with robust monitoring
        start_time = time.time()

        while time.time() - start_time < 30:
            # Check if process died
            if self.process.poll() is not None:
                raise RuntimeError("PGlite process died during startup")

            # Unix socket readiness check
            if self.ready_flag.exists():
                self.logger.info("PGlite socket created, server should be ready...")
                break

            time.sleep(0.5)
        else:
            # Timeout - cleanup and raise error
            if self.process and self.process.poll() is None:
                self.logger.warning("PGlite server startup timeout, terminating...")
                self.process.terminate()
                self.process.wait(timeout=5)

            raise RuntimeError("PGlite server failed to start within 30 seconds")

    def stop(self) -> None:
        """Stop the PGlite server."""
        if self.process is None:
            return

        self.ready_flag.unlink(missing_ok=True)

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

                self.process.wait(timeout=2)
                self.logger.info("PGlite server stopped forcefully")

        except Exception as e:
            self.logger.warning(f"Error stopping PGlite: {e}")
        finally:
            self.process = None

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

    def get_psycopg_uri(self) -> str:
        """Get the database URI for psycopg usage.

        Returns:
            PostgreSQL URI string compatible with psycopg

        Raises:
            RuntimeError: If PGlite server is not running
        """
        if self.socket_path:
            socket_dir = self.socket_path.parent
            return f"postgresql://postgres:postgres@/postgres?host={socket_dir}"

        else:
            return "postgresql://postgres:postgres@localhost:5432/postgres"
