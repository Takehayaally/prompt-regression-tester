from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path


def load_suite(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "tests" not in payload or not isinstance(payload["tests"], list):
        raise ValueError("Suite JSON must contain a tests list.")
    return payload


def run_test(test: dict) -> dict:
    output = str(test.get("output", ""))
    lower_output = output.lower()
    failures: list[str] = []

    for expected in test.get("expected_contains", []):
        if str(expected).lower() not in lower_output:
            failures.append(f"Missing expected text: {expected}")

    for forbidden in test.get("forbidden_contains", []):
        if str(forbidden).lower() in lower_output:
            failures.append(f"Found forbidden text: {forbidden}")

    for pattern in test.get("expected_regex", []):
        if not re.search(pattern, output, flags=re.IGNORECASE | re.MULTILINE):
            failures.append(f"Regex did not match: {pattern}")

    max_chars = test.get("max_chars")
    if max_chars is not None and len(output) > int(max_chars):
        failures.append(f"Output length {len(output)} exceeds max_chars {max_chars}")

    min_chars = test.get("min_chars")
    if min_chars is not None and len(output) < int(min_chars):
        failures.append(f"Output length {len(output)} is below min_chars {min_chars}")

    return {
        "name": test.get("name", "unnamed"),
        "passed": not failures,
        "failures": failures,
        "chars": len(output),
    }


def render_html(suite_name: str, results: list[dict]) -> str:
    passed = sum(1 for result in results if result["passed"])
    rows = []
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        failures = "<br>".join(html.escape(item) for item in result["failures"]) or "-"
        rows.append(
            "<tr>"
            f"<td>{html.escape(result['name'])}</td>"
            f"<td>{status}</td>"
            f"<td>{result['chars']}</td>"
            f"<td>{failures}</td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>{html.escape(suite_name)} Prompt Regression Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2937; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: left; }}
th {{ background: #f3f4f6; }}
</style>
<h1>{html.escape(suite_name)} Prompt Regression Report</h1>
<p>{passed}/{len(results)} tests passed.</p>
<table>
<thead><tr><th>Test</th><th>Status</th><th>Chars</th><th>Failures</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run saved prompt-output regression tests.")
    parser.add_argument("--suite", required=True, help="Path to suite JSON.")
    parser.add_argument("--html-out", default="prompt-regression-report.html")
    parser.add_argument("--json-out", default="prompt-regression-report.json")
    args = parser.parse_args(argv)

    suite = load_suite(Path(args.suite))
    results = [run_test(test) for test in suite["tests"]]
    suite_name = suite.get("suite", "Prompt Suite")

    Path(args.json_out).write_text(
        json.dumps({"suite": suite_name, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    Path(args.html_out).write_text(render_html(suite_name, results), encoding="utf-8")

    failed = [result for result in results if not result["passed"]]
    print(f"{len(results) - len(failed)}/{len(results)} tests passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
