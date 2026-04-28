"""
Engineer Agent Tools
=====================

Code generation, linting, and file system tools for the Engineer Agent.
"""

import subprocess
from pathlib import Path


def write_pom(file_path: str, content: str) -> str:
    """Write a Page Object Model TypeScript file to automation/pages/.

    Args:
        file_path: Relative path within automation/pages/ (e.g., "login.page.ts")
        content: Full TypeScript class content.

    Returns:
        Confirmation message with the written file path.
    """
    base = Path(__file__).parent.parent.parent / "automation" / "pages"
    target = base / file_path

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"Written POM: automation/pages/{file_path}"


def write_step_def(file_path: str, content: str) -> str:
    """Write a Step Definition TypeScript file to automation/step_definitions/.

    Args:
        file_path: Relative path within automation/step_definitions/ (e.g., "login.steps.ts")
        content: Full TypeScript step definition content.

    Returns:
        Confirmation message with the written file path.
    """
    base = Path(__file__).parent.parent.parent / "automation" / "step_definitions"
    target = base / file_path

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"Written step defs: automation/step_definitions/{file_path}"


def write_feature(file_path: str, content: str) -> str:
    """Write a Gherkin feature file to automation/features/.

    Args:
        file_path: Relative path within automation/features/ (e.g., "login.feature")
        content: Full Gherkin feature file content.

    Returns:
        Confirmation message with the written file path.
    """
    base = Path(__file__).parent.parent.parent / "automation" / "features"
    target = base / file_path

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"Written feature: automation/features/{file_path}"


def run_typecheck(working_dir: str = "automation") -> str:
    """Run TypeScript type-check on the automation framework.

    Args:
        working_dir: Directory to run tsc in (relative to project root).

    Returns:
        'PASS' message or error output from tsc.
    """
    target = Path(__file__).parent.parent.parent / working_dir
    if not (target / "tsconfig.json").exists():
        return f"ERROR: tsconfig.json not found in {working_dir}"

    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit"],
            cwd=str(target),
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return "PASS: TypeScript type-check succeeded"
        return f"FAIL: Type errors found:\n{result.stdout}\n{result.stderr}"
    except FileNotFoundError:
        return "ERROR: npx not found. Run 'npm install' in automation/ first."
    except subprocess.TimeoutExpired:
        return "ERROR: tsc timed out after 60s"
