"""
02_crewai_guard.py — EnterpriseActionGuard wrapping a mock tool.

Demonstrates how EnterpriseActionGuard enforces ActionPolicy on a CrewAI-style
tool, blocking unauthorized actions and raising PolicyViolationError.

Two scenarios:
  1. An "export_data" tool guarded by a policy that denies it — BLOCKED.
  2. A "read_record" tool guarded by a policy that allows it — ALLOWED.

No crewai package is required; the guard is duck-typed. If crewai is installed,
the import path works without modification.

Run:
    python examples/02_crewai_guard.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# EnterpriseActionGuard calls _import_crewai() in __init__, which raises
# ImportError when crewai is not installed.  We patch the check so the
# adapter can be demonstrated without the optional SDK dependency.
import regulated_ai_governance.adapters.crewai as _crewai_module
from regulated_ai_governance.policy import ActionPolicy

try:
    import crewai  # noqa: F401
except ImportError:
    # Replace the check with a no-op so __init__ proceeds without crewai.
    _crewai_module._import_crewai = lambda: None  # type: ignore[attr-defined]

from regulated_ai_governance.adapters.crewai import (
    EnterpriseActionGuard,
    PolicyViolationError,
)


class MockTool:
    """
    Duck-typed stand-in for a CrewAI BaseTool.

    EnterpriseActionGuard only requires .name, .description, and ._run().
    """

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._run_call_count = 0

    def _run(self, *args, **kwargs) -> str:
        self._run_call_count += 1
        return f"Tool '{self.name}' executed successfully."


def main() -> None:
    print("=" * 62)
    print("EnterpriseActionGuard — CrewAI Tool Guard Demo")
    print("=" * 62)

    # Policy: allow read_record, explicitly deny export_data
    policy = ActionPolicy(
        allowed_actions={"read_record", "generate_summary"},
        denied_actions={"export_data"},
        require_all_allowed=True,
    )

    print(f"\nPolicy: allowed={sorted(policy.allowed_actions)}  denied={sorted(policy.denied_actions)}")

    # --- Scenario 1: export_data is blocked ---
    print()
    print("Scenario 1 — export_data (should be BLOCKED)")
    print("-" * 62)

    export_tool = MockTool(name="export_data", description="Exports student records in bulk.")
    guarded_export = EnterpriseActionGuard(
        tool=export_tool,
        policy=policy,
        policy_name="student-record-policy",
        regulation_citation="FERPA 34 CFR § 99.31(a)(1)",
    )

    print(f"  Tool name:     {guarded_export.name!r}")
    print(f"  Tool desc:     {guarded_export.description!r}")
    print("  Calling guarded_export._run()...")
    try:
        result = guarded_export._run()
        print(f"  Unexpected success: {result}")
    except PolicyViolationError as exc:
        print("  PolicyViolationError raised (expected):")
        print(f"    {exc}")
    print(f"  Underlying tool._run() call count: {export_tool._run_call_count} (expected 0)")
    assert export_tool._run_call_count == 0, "Guard failed: underlying tool was called despite block"

    # --- Scenario 2: read_record is allowed ---
    print()
    print("Scenario 2 — read_record (should be ALLOWED)")
    print("-" * 62)

    read_tool = MockTool(name="read_record", description="Reads a student academic record.")
    guarded_read = EnterpriseActionGuard(
        tool=read_tool,
        policy=policy,
        policy_name="student-record-policy",
        regulation_citation="FERPA 34 CFR § 99.31(a)(1)",
    )

    print(f"  Tool name:     {guarded_read.name!r}")
    print("  Calling guarded_read._run()...")
    try:
        result = guarded_read._run()
        print(f"  Result: {result!r}")
    except PolicyViolationError as exc:
        print(f"  Unexpected PolicyViolationError: {exc}")
    print(f"  Underlying tool._run() call count: {read_tool._run_call_count} (expected 1)")
    assert read_tool._run_call_count == 1, "Guard failed: allowed tool was not called"

    print()
    print("All assertions passed.")
    print("  - export_data was blocked before _run() was reached")
    print("  - read_record was allowed and its _run() was executed")
    print("\nDone.")


if __name__ == "__main__":
    main()
