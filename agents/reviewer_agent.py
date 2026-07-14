import re
from pathlib import Path
from typing import List, Optional, Tuple


class ReviewerAgent:
    """Review generated Appium scripts for common best-practice issues."""

    def __init__(self, project_root: Optional[Path | str] = None) -> None:
        self.project_root = Path(project_root or Path(__file__).resolve().parents[1])
        self.input_dir = self.project_root / "artifacts" / "generated_appium_scripts"
        self.output_dir = self.project_root / "artifacts" / "review_reports"

    def review_scripts(self, input_dir: Optional[Path | str] = None, output_dir: Optional[Path | str] = None) -> List[Path]:
        """Review every generated Appium script and write a Markdown report for each."""
        source_dir = Path(input_dir or self.input_dir)
        destination_dir = Path(output_dir or self.output_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)

        reviewed_files: List[Path] = []
        for script_path in sorted(source_dir.glob("*.py")):
            report_path = self._review_script(script_path, destination_dir)
            reviewed_files.append(report_path)

        print(f"Reviewed {len(reviewed_files)} scripts successfully.")
        return reviewed_files

    def _review_script(self, script_path: Path, output_dir: Path) -> Path:
        """Inspect one script and write a markdown review report."""
        content = script_path.read_text(encoding="utf-8")
        issues = self._collect_issues(content)
        report_path = output_dir / f"{script_path.stem}_review.md"
        report_path.write_text(self._format_report(script_path, content, issues), encoding="utf-8")
        return report_path

    def _collect_issues(self, content: str) -> List[Tuple[str, str]]:
        """Collect review findings as (category, message) tuples."""
        issues: List[Tuple[str, str]] = []

        if re.search(r"\bsleep\s*\(", content):
            issues.append(("Hardcoded sleep", "The script uses time.sleep(), which can make tests flaky."))

        if re.search(r"find_element\s*\(\s*['\"]//", content):
            issues.append(("XPath usage", "XPath locators were detected; prefer UiAutomator2 selectors instead."))

        if re.search(r"WebDriverWait", content):
            issues.append(("WebDriverWait", "The script uses WebDriverWait, which is good for stability."))
        else:
            issues.append(("Missing WebDriverWait", "The script does not use WebDriverWait for explicit waits."))

        if re.search(r"AppiumBy", content):
            issues.append(("AppiumBy", "The script uses AppiumBy, which is good for Appium-native locators."))
        else:
            issues.append(("Missing AppiumBy", "The script does not import or use AppiumBy."))

        if self._count_repeated_code_blocks(content) > 1:
            issues.append(("Repeated code", "The script repeats similar interaction logic and could be simplified."))

        if re.search(r"def\s+(tap|type|scroll)\s*\(", content):
            issues.append(("Method names", "The script already uses helper methods for tap/type/scroll."))
        else:
            issues.append(("Poor method names", "The script could benefit from helper methods with clearer names."))

        if re.search(r"self\.tap\(|self\.type\(|self\.scroll\(", content):
            issues.append(("Tap usage", "Helper methods are used, which is preferable to repeated inline actions."))
        else:
            issues.append(("Tap usage", "Inline tap actions were detected; consider helper methods for clarity."))

        if re.search(r"tap\s*\(.*text|tap\s*\(.*image|tap\s*\(.*icon", content, re.IGNORECASE):
            issues.append(("Unnecessary tap", "The script may be tapping text or image elements that should be verified or scrolled instead."))

        return issues

    def _count_repeated_code_blocks(self, content: str) -> int:
        """Estimate repeated code by counting repeated lines that start with self."""
        lines = [line.strip() for line in content.splitlines() if line.strip().startswith("self.")]
        return sum(1 for line in lines if lines.count(line) > 1)

    def _format_report(self, script_path: Path, content: str, issues: List[Tuple[str, str]]) -> str:
        """Render a Markdown review report for one script."""
        lines = [
            f"# Review Report: {script_path.name}",
            "",
            "## Summary",
            "",
            f"- Script reviewed: {script_path.name}",
            f"- Issues detected: {len(issues)}",
            "",
            "## Findings",
            "",
        ]

        for category, message in issues:
            lines.append(f"- **{category}**: {message}")

        lines.extend([
            "",
            "## Notes",
            "",
            "- Prefer UiAutomator2 selectors over XPath.",
            "- Use WebDriverWait with explicit waits instead of hardcoded sleeps.",
            "- Keep page actions in helper methods to reduce repetition.",
            "- Avoid tapping static text or image elements unless the UI requires it.",
        ])

        return "\n".join(lines) + "\n"


def main() -> List[Path]:
    """Review every generated Appium script and write Markdown reports."""
    agent = ReviewerAgent()
    agent.output_dir.mkdir(parents=True, exist_ok=True)
    return agent.review_scripts()


if __name__ == "__main__":
    main()
