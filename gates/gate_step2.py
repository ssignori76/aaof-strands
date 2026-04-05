"""Gate Step 2 — Plan: verify the human approved the implementation plan."""
from typing import List

from gates.base import BaseGate, GateResult


class GateStep2(BaseGate):
    """Gate checks for Step 2 (Plan).

    This step requires explicit human approval tracked in the session state.
    The orchestrator sets VAR_HUMAN_APPROVAL_STEP2 after the user confirms.
    """

    def check_all(self) -> List[GateResult]:
        approved = self.state.get("VAR_HUMAN_APPROVAL_STEP2", False)
        if not approved:
            return [
                GateResult(
                    "HUMAN_APPROVAL",
                    False,
                    "❌ Human approval not recorded for Step 2",
                )
            ]
        return [GateResult("HUMAN_APPROVAL", True, "✅ Human approved the plan")]
