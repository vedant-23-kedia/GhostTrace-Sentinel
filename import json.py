import json
import os
from datetime import datetime

CONTEXT_PATH = "current_context.json"
REPORT_PATH = "latest_report.json"


def load_context():
    if os.path.exists(CONTEXT_PATH):
        with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def write_report(status, reason, developer="Unknown"):
    report = {
        "status": status,
        "reason": reason,
        "developer": developer,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print("STATUS:", status)
    print("REASON:", reason)


def run_mock_audit():
    context = load_context()

    developer = context.get("developer", "Unknown")
    requirement = context.get("requirement", "")

    if not requirement.strip():
        write_report(
            "FAIL",
            "No requirement found. Please sync requirement first from dashboard.",
            developer
        )
        return

    # Simple demo logic
    requirement_lower = requirement.lower()

    if "payment" in requirement_lower or "pay now" in requirement_lower:
        write_report(
            "PASS",
            "Mock audit passed. Requirement was found and business rules are ready for validation. Ollama integration can be enabled later.",
            developer
        )
    else:
        write_report(
            "FAIL",
            "Mock audit failed. Requirement does not contain expected payment/business rule keywords.",
            developer
        )


if __name__ == "__main__":
    run_mock_audit()