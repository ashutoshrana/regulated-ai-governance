"""
01_basic_policy_enforcement.py — Basic ActionPolicy allow/deny enforcement.

Demonstrates how ActionPolicy controls which actions an AI agent may execute:
  - Allowed actions proceed without error
  - Denied actions raise PolicyViolationError
  - Unlisted actions are also denied when require_all_allowed=True

Actions tested:
  Allowed:  read_record, generate_summary
  Blocked:  delete_record, export_bulk

Run:
    python examples/01_basic_policy_enforcement.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from regulated_ai_governance.policy import ActionPolicy
from regulated_ai_governance.adapters.crewai import PolicyViolationError


def attempt_action(policy: ActionPolicy, action_name: str) -> None:
    """Check a single action against the policy and print the outcome."""
    permitted, reason = policy.permits(action_name)
    if permitted:
        print(f"  ALLOWED  {action_name!r:<22} — executing action")
    else:
        print(f"  BLOCKED  {action_name!r:<22} — {reason}")
        raise PolicyViolationError(
            action=action_name,
            policy_name="student-record-access-policy",
        )


def main() -> None:
    print("=" * 62)
    print("ActionPolicy — Basic Enforcement Demo")
    print("=" * 62)

    policy = ActionPolicy(
        allowed_actions={"read_record", "generate_summary"},
        denied_actions={"delete_record", "export_bulk"},
        require_all_allowed=True,
    )

    print(f"\nPolicy configuration:")
    print(f"  allowed_actions:    {sorted(policy.allowed_actions)}")
    print(f"  denied_actions:     {sorted(policy.denied_actions)}")
    print(f"  require_all_allowed: {policy.require_all_allowed}")

    test_actions = [
        ("read_record", True),
        ("generate_summary", True),
        ("delete_record", False),
        ("export_bulk", False),
        ("send_email", False),  # unlisted — denied by require_all_allowed
    ]

    print(f"\nTesting {len(test_actions)} actions:")
    print("-" * 62)

    results: list[tuple[str, bool, bool]] = []
    for action_name, expected_allowed in test_actions:
        try:
            attempt_action(policy, action_name)
            results.append((action_name, True, expected_allowed))
        except PolicyViolationError as exc:
            print(f"           PolicyViolationError: {exc}")
            results.append((action_name, False, expected_allowed))

    # Summary
    print()
    print("Summary:")
    print(f"  {'Action':<22} {'Expected':<12} {'Actual':<12} {'Match'}")
    print("  " + "-" * 54)
    all_match = True
    for action_name, actual, expected in results:
        expected_str = "ALLOWED" if expected else "BLOCKED"
        actual_str = "ALLOWED" if actual else "BLOCKED"
        match = expected == actual
        marker = "OK" if match else "MISMATCH"
        if not match:
            all_match = False
        print(f"  {action_name:<22} {expected_str:<12} {actual_str:<12} {marker}")

    print()
    if all_match:
        print("All policy decisions matched expectations.")
    else:
        print("WARNING: some policy decisions did not match expectations.")

    print("\nDone.")


if __name__ == "__main__":
    main()
