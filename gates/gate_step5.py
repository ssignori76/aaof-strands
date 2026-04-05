"""Gate Step 5 — Validate: THE critical anti-cheating gate.

This gate makes real HTTP requests and inspects the filesystem directly.
The AI agent has no way to fake these results.
"""
import json
import os
import re
import subprocess
from pathlib import Path
from typing import List

import requests

from gates.base import BaseGate, GateResult


class GateStep5(BaseGate):
    """Anti-cheat gate for Step 5 (Validate).

    Checks performed:
      POST-5.2  test_playbook.md exists and is not empty
      POST-5.3  test_results.md contains required section headers
      POST-5.6  test_runner.sh exists and is executable
      SMOKE     Real HTTP GET to http://localhost:3000/ — not a default page
      K8S       (optional) All K8s pods Running
      XREF      Files cited in playbook actually exist on disk
    """

    def check_all(self) -> List[GateResult]:
        results = []

        # POST-5.2: test_playbook.md exists and not empty
        results.append(self.check_file_exists("output/test_playbook.md", min_size=100))

        # POST-5.3: test_results.md exists with required sections
        results.append(
            self.check_file_contains("output/test_results.md", ["Test ID", "Status"])
        )

        # POST-5.6: test_runner.sh exists and is executable
        runner = Path("output/test_runner.sh")
        if runner.exists() and os.access(runner, os.X_OK):
            results.append(
                GateResult("TEST_RUNNER", True, "✅ test_runner.sh executable")
            )
        else:
            results.append(
                GateResult(
                    "TEST_RUNNER",
                    False,
                    "❌ test_runner.sh missing or not executable",
                )
            )

        # SMOKE TEST: Real HTTP check — agent cannot fake this
        results.append(self._smoke_test())

        # K8S check if K8S is a deploy target
        if "K8S" in self.config.get("deploy_targets", []):
            results.append(self._k8s_check())

        # Anti-hallucination: verify files referenced in playbook actually exist
        results.extend(self._cross_reference_check())

        return results

    def _smoke_test(self) -> GateResult:
        """Perform a real HTTP smoke test.

        The agent cannot fake an HTTP 200 response from a running service.
        We also reject generic default pages (nginx, Apache) to ensure the
        actual application is running.
        """
        try:
            resp = requests.get("http://localhost:3000/", timeout=10)
            default_pages = ["It works!", "Welcome to nginx", "Apache2 Default"]
            if any(d in resp.text for d in default_pages):
                return GateResult(
                    "SMOKE_TEST",
                    False,
                    f"❌ Default page detected — app not properly configured. Body: {resp.text[:200]}",
                )
            if resp.status_code == 200:
                return GateResult("SMOKE_TEST", True, "✅ Smoke test passed (200 OK)")
            return GateResult(
                "SMOKE_TEST", False, f"❌ Unexpected status: {resp.status_code}"
            )
        except Exception as exc:  # pylint: disable=broad-except
            return GateResult("SMOKE_TEST", False, f"❌ Connection failed: {exc}")

    def _k8s_check(self) -> GateResult:
        """Verify K8s deployment — all pods must be Running."""
        try:
            result = subprocess.run(
                ["kubectl", "get", "pods", "-o", "json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                return GateResult(
                    "K8S_PODS", False, f"❌ kubectl failed: {result.stderr.strip()}"
                )
            pods = json.loads(result.stdout)
            running = [
                p
                for p in pods.get("items", [])
                if p.get("status", {}).get("phase") == "Running"
            ]
            total = len(pods.get("items", []))
            if total == 0:
                return GateResult("K8S_PODS", False, "❌ No pods found")
            if len(running) == total:
                return GateResult(
                    "K8S_PODS", True, f"✅ All {total} pod(s) Running"
                )
            return GateResult(
                "K8S_PODS",
                False,
                f"❌ {len(running)}/{total} pods Running",
            )
        except Exception as exc:  # pylint: disable=broad-except
            return GateResult("K8S_PODS", False, f"❌ K8s check failed: {exc}")

    def _cross_reference_check(self) -> List[GateResult]:
        """Anti-hallucination check: every file cited in the playbook must exist.

        Looks for patterns like ``output/foo.sh`` or ``./bar.json`` inside
        the test_playbook.md and confirms each referenced file is on disk.
        """
        results: List[GateResult] = []
        playbook = Path("output/test_playbook.md")
        if not playbook.exists():
            return results

        content = playbook.read_text(encoding="utf-8")
        refs = re.findall(
            r"(?:output/|\./)([a-zA-Z0-9_\-./]+\.(?:sh|py|js|json|yml|yaml))",
            content,
        )
        for ref in set(refs):
            ref_path = (
                Path("output") / ref
                if not ref.startswith("output/")
                else Path(ref)
            )
            if not ref_path.exists():
                results.append(
                    GateResult(
                        f"XREF_{ref}",
                        False,
                        f"❌ HALLUCINATION: {ref} cited in playbook but does not exist!",
                    )
                )
            else:
                results.append(
                    GateResult(f"XREF_{ref}", True, f"✅ {ref} exists")
                )
        return results
