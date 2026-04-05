"""Base gate classes shared by all step gates."""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class GateResult:
    """Result of a single gate check."""

    gate_id: str
    passed: bool
    message: str


class BaseGate:
    """Abstract base class for all step gates.

    Every gate receives the loaded config dict and the SessionState instance
    so it can read/write workflow variables as needed.
    """

    def __init__(self, config: dict, state) -> None:
        self.config = config
        self.state = state

    # ------------------------------------------------------------------
    # Reusable helper checks
    # ------------------------------------------------------------------

    def check_file_exists(self, path: str, min_size: int = 1) -> GateResult:
        """Verify that *path* exists and is at least *min_size* bytes."""
        p = Path(path)
        if not p.exists():
            return GateResult(f"FILE_{p.name}", False, f"❌ Not found: {path}")
        if p.stat().st_size < min_size:
            return GateResult(
                f"FILE_{p.name}", False, f"❌ Empty/too small: {path}"
            )
        return GateResult(f"FILE_{p.name}", True, f"✅ OK: {path}")

    def check_file_contains(self, path: str, required_strings: list) -> GateResult:
        """Verify that *path* exists and contains all *required_strings*."""
        p = Path(path)
        if not p.exists():
            return GateResult(
                f"CONTENT_{p.name}", False, f"❌ Not found: {path}"
            )
        content = p.read_text(encoding="utf-8")
        missing = [s for s in required_strings if s not in content]
        if missing:
            return GateResult(
                f"CONTENT_{p.name}",
                False,
                f"❌ Missing in {path}: {missing}",
            )
        return GateResult(
            f"CONTENT_{p.name}", True, f"✅ Content OK: {path}"
        )

    def check_all(self) -> List[GateResult]:
        """Run all checks for this gate.  Must be overridden by subclasses."""
        raise NotImplementedError

    def evaluate(self) -> Tuple[bool, List[GateResult]]:
        """Run check_all() and return (overall_passed, results_list)."""
        results = self.check_all()
        passed = all(r.passed for r in results)
        return passed, results
