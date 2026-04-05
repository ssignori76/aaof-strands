"""Gate Step 1 — Resolution: confirm versions and security profile are set."""
from typing import List

from gates.base import BaseGate, GateResult


class GateStep1(BaseGate):
    """Gate checks for Step 1 (Resolution)."""

    def check_all(self) -> List[GateResult]:
        results = []
        results.append(self._check_confirmed_versions())
        results.append(self._check_security_profile())
        return results

    def _check_confirmed_versions(self) -> GateResult:
        """Verify that VAR_CONFIRMED_VERSIONS was populated by the agent."""
        versions = self.state.get("VAR_CONFIRMED_VERSIONS", {})
        if not versions:
            return GateResult(
                "CONFIRMED_VERSIONS",
                False,
                "❌ VAR_CONFIRMED_VERSIONS is empty — agent must confirm library versions",
            )
        count = len(versions)
        return GateResult(
            "CONFIRMED_VERSIONS",
            True,
            f"✅ Confirmed {count} version(s): {list(versions.keys())}",
        )

    def _check_security_profile(self) -> GateResult:
        """Verify that VAR_SECURITY_PROFILE was set by the agent."""
        profile = self.state.get("VAR_SECURITY_PROFILE", "")
        if not profile:
            return GateResult(
                "SECURITY_PROFILE",
                False,
                "❌ VAR_SECURITY_PROFILE is empty — agent must define security profile",
            )
        return GateResult(
            "SECURITY_PROFILE", True, f"✅ Security profile: {profile}"
        )
