"""
Detective Agent Tools
======================

Trace parsing and log analysis tools for the Detective Agent.
"""

import re
import zipfile
from pathlib import Path


def parse_trace_zip(trace_path: str) -> str:
    """Extract and summarize the contents of a Playwright trace.zip.

    Args:
        trace_path: Path to the Playwright trace.zip file.

    Returns:
        Text summary of trace contents, or error message if parsing fails.
    """
    path = Path(trace_path)
    if not path.exists():
        return f"ERROR: Trace file not found: {trace_path}"
    if not path.suffix == ".zip":
        return f"ERROR: Expected a .zip file, got: {trace_path}"

    try:
        with zipfile.ZipFile(path, "r") as zf:
            file_list = zf.namelist()
            summary_parts = [f"Trace archive: {path.name}", f"Files: {len(file_list)}"]

            # Try to read the trace.json entry
            trace_entries = [f for f in file_list if f.endswith(".json")]
            for entry in trace_entries[:3]:
                try:
                    content = zf.read(entry).decode("utf-8", errors="replace")
                    summary_parts.append(f"\n--- {entry} (first 2000 chars) ---\n{content[:2000]}")
                except Exception:  # noqa: BLE001
                    summary_parts.append(f"\n--- {entry}: unreadable ---")

            return "\n".join(summary_parts)
    except zipfile.BadZipFile:
        return f"ERROR: Invalid or corrupt zip file: {trace_path}"
    except Exception as e:  # noqa: BLE001
        return f"ERROR: {type(e).__name__}: {e}"


def parse_ci_log(log_content: str) -> dict:
    """Parse CI/CD log output to extract failure signals.

    Args:
        log_content: Raw CI/CD log text (from GitHub Actions, Azure Pipelines, etc.)

    Returns:
        Dict with extracted failure signals:
        - error_lines: list of lines containing errors
        - timeout_detected: bool
        - selector_errors: list of failed selectors
        - assertion_errors: list of failed assertions
        - env_errors: list of infrastructure/network errors
    """
    lines = log_content.split("\n")

    error_lines = [l for l in lines if re.search(r"error|Error|FAIL|fail", l, re.IGNORECASE)]
    timeout_detected = any("timeout" in l.lower() or "timed out" in l.lower() for l in lines)
    selector_errors = [
        l for l in lines if re.search(r"locator|selector|element.*not found|getByTestId|getByRole", l, re.IGNORECASE)
    ]
    assertion_errors = [l for l in lines if re.search(r"expect|assert|toBe|toEqual|toContain", l, re.IGNORECASE)]
    env_errors = [
        l for l in lines if re.search(r"ECONNREFUSED|503|502|504|connection reset|network", l, re.IGNORECASE)
    ]

    return {
        "error_lines": error_lines[:20],
        "timeout_detected": timeout_detected,
        "selector_errors": selector_errors[:10],
        "assertion_errors": assertion_errors[:10],
        "env_errors": env_errors[:10],
        "total_lines": len(lines),
    }


def classify_failure(parsed_log: dict) -> str:
    """Heuristically classify a failure from parsed log signals.

    Args:
        parsed_log: Output from parse_ci_log.

    Returns:
        Classification string: LOCATOR_STALE | DATA_MISMATCH | TIMING_FLAKE |
                               ENV_FAILURE | LOGIC_CHANGE | UNKNOWN
    """
    if parsed_log.get("env_errors"):
        return "ENV_FAILURE"
    if parsed_log.get("selector_errors") and not parsed_log.get("assertion_errors"):
        return "LOCATOR_STALE"
    if parsed_log.get("timeout_detected") and not parsed_log.get("selector_errors"):
        return "TIMING_FLAKE"
    if parsed_log.get("assertion_errors") and not parsed_log.get("selector_errors"):
        return "LOGIC_CHANGE"
    if parsed_log.get("selector_errors") and parsed_log.get("assertion_errors"):
        return "DATA_MISMATCH"
    return "UNKNOWN"
