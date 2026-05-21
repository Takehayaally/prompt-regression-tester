# Prompt Regression Tester

Run local prompt-output regression checks and generate JSON/HTML reports. This MVP does not call any LLM provider; it validates saved outputs so teams can catch prompt behavior changes after model, prompt, or retrieval updates.

By TinyOps Tools. Support: q749381667@gmail.com.

## Usage

```powershell
python products/prompt-regression-tester/prompt_regression_tester.py --suite products/prompt-regression-tester/examples/suite.json --html-out products/prompt-regression-tester/examples/report.html --json-out products/prompt-regression-tester/examples/report.json
```

The process exits with code `1` if any regression test fails.

## Example Output

The `examples/` folder includes:

- `report.json`
- `report.html`

## Paid Bundle

Launch price: $19 on Gumroad:

https://5444798427684.gumroad.com/l/prompt-regression-tester

The paid bundle includes batch examples, report templates, paid bonus suites, and a commercial-use license.
