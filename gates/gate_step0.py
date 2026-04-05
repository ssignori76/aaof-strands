"""Gate Step 0 — Bootstrap: verify Docker is installed and rules/ has content."""
import subprocess
from pathlib import Path
from typing import List

from gates.base import BaseGate, GateResult


class GateStep0(BaseGate):
    """Gate checks for Step 0 (Bootstrap)."""

    def check_all(self) -> List[GateResult]:
        results = []
        results.append(self._check_docker())
        results.append(self._check_rules_directory())
        return results

    def _check_docker(self) -> GateResult:
        """Verify Docker is installed and accessible."""
        try:
            proc = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if proc.returncode == 0:
                version = proc.stdout.strip()
                self.state.set("VAR_DOCKER_INSTALLED", True)
                return GateResult("DOCKER_VERSION", True, f"✅ Docker found: {version}")
            return GateResult(
                "DOCKER_VERSION", False, f"❌ docker --version failed: {proc.stderr.strip()}"
            )
        except FileNotFoundError:
            return GateResult(
                "DOCKER_VERSION",
                False,
                "❌ Docker not found. Install Docker Desktop: https://www.docker.com/products/docker-desktop/",
            )
        except Exception as exc:  # pylint: disable=broad-except
            return GateResult("DOCKER_VERSION", False, f"❌ Docker check error: {exc}")

    def _check_rules_directory(self) -> GateResult:
        """Verify that the rules/ directory contains at least one .md file."""
        rules_dir = Path("rules")
        if not rules_dir.is_dir():
            return GateResult("RULES_DIR", False, "❌ rules/ directory not found")
        md_files = list(rules_dir.glob("*.md"))
        if not md_files:
            return GateResult("RULES_DIR", False, "❌ rules/ directory has no .md files")
        return GateResult(
            "RULES_DIR", True, f"✅ rules/ has {len(md_files)} rule file(s)"
        )
