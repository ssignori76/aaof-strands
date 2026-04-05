"""Gate Step 4 — Implement: verify output files exist and contracts pass."""
from pathlib import Path
from typing import List

from gates.base import BaseGate, GateResult


class GateStep4(BaseGate):
    """Gate checks for Step 4 (Implement)."""

    def check_all(self) -> List[GateResult]:
        results = []
        results.append(self._check_output_has_files())
        results.append(self._check_contract())
        return results

    def _check_output_has_files(self) -> GateResult:
        """Verify the output/ directory contains at least one generated file."""
        output_dir = Path("output")
        if not output_dir.is_dir():
            return GateResult("OUTPUT_DIR", False, "❌ output/ directory not found")
        files = [f for f in output_dir.iterdir() if f.is_file() and f.name != ".gitkeep"]
        if not files:
            return GateResult("OUTPUT_FILES", False, "❌ output/ directory is empty")
        return GateResult(
            "OUTPUT_FILES", True, f"✅ output/ has {len(files)} generated file(s)"
        )

    def _check_contract(self) -> GateResult:
        """Verify the contract check result stored by the agent."""
        contract_result = self.state.get("VAR_CONTRACT_CHECK", "")
        if contract_result.upper() != "PASS":
            return GateResult(
                "CONTRACT_CHECK",
                False,
                f"❌ VAR_CONTRACT_CHECK = '{contract_result}' (expected PASS)",
            )
        return GateResult("CONTRACT_CHECK", True, "✅ Contract check: PASS")
