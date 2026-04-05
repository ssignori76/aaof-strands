"""Gate Step 7 — Consolidate: verify docs updated and specs archived."""
from pathlib import Path
from typing import List

from gates.base import BaseGate, GateResult


class GateStep7(BaseGate):
    """Gate checks for Step 7 (Consolidate)."""

    def check_all(self) -> List[GateResult]:
        results = []
        results.append(self._check_deployed_state())
        results.append(self._check_changelog())
        results.append(self._check_specs_archived())
        return results

    def _check_deployed_state(self) -> GateResult:
        """Verify that deployed_state.json has been created/updated."""
        return self.check_file_exists("output/deployed_state.json", min_size=10)

    def _check_changelog(self) -> GateResult:
        """Verify that changelog.md has been created/updated."""
        return self.check_file_exists("output/changelog.md", min_size=50)

    def _check_specs_archived(self) -> GateResult:
        """Verify that processed specs were moved to specs/history/."""
        history_dir = Path("specs/history")
        if not history_dir.is_dir():
            return GateResult(
                "SPECS_ARCHIVED", False, "❌ specs/history/ directory not found"
            )
        archived = [
            f for f in history_dir.iterdir()
            if f.is_file() and f.suffix == ".md"
        ]
        if not archived:
            return GateResult(
                "SPECS_ARCHIVED",
                False,
                "❌ No archived spec files found in specs/history/",
            )
        return GateResult(
            "SPECS_ARCHIVED",
            True,
            f"✅ {len(archived)} spec(s) archived to specs/history/",
        )
