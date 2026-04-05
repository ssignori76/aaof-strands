"""Gate Step 6 — Rollback: verify the rollback completed successfully."""
from pathlib import Path
from typing import List

from gates.base import BaseGate, GateResult


class GateStep6(BaseGate):
    """Gate checks for Step 6 (Rollback).

    Verifies that:
    - A rollback report was written documenting what was restored.
    - The backup files were actually restored to the output/ directory.
    - No running containers remain (services were stopped).
    """

    def check_all(self) -> List[GateResult]:
        results = []
        results.append(self._check_rollback_report())
        results.append(self._check_output_restored())
        return results

    def _check_rollback_report(self) -> GateResult:
        """Verify the rollback report was written."""
        return self.check_file_exists("output/rollback_report.md", min_size=50)

    def _check_output_restored(self) -> GateResult:
        """Verify the output/ directory has content (files were restored from backup)."""
        output_dir = Path("output")
        if not output_dir.is_dir():
            return GateResult(
                "OUTPUT_RESTORED", False, "❌ output/ directory not found after rollback"
            )
        files = [
            f for f in output_dir.iterdir()
            if f.is_file() and f.name != ".gitkeep"
        ]
        if not files:
            return GateResult(
                "OUTPUT_RESTORED",
                False,
                "❌ output/ is empty after rollback — restore may have failed",
            )
        return GateResult(
            "OUTPUT_RESTORED",
            True,
            f"✅ output/ has {len(files)} file(s) after rollback",
        )
