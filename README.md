# AI Powered Mobile Test Automation Generator

A three-step pipeline that turns mobile app screenshots into manual test cases, then into a runnable
Android Appium Page Object Model test framework, using LLMs.

---

## What This Repo Does

- Turns a mobile app screenshot into structured screen data (Vision Agent)
- Turns that screen data into manual test cases (Test Case Agent)
- Turns those test cases into runnable Android Appium test scripts, following
  Page Object Model - locators + actions in one file, test steps in another
  (Appium Script Generator Agent)
- Works with OpenAI directly, any OpenAI-compatible LLM gateway (including an
  internal company LLM), or fully offline in mock mode with no API key
- Also includes a FastAPI-backed review/execution layer (see below) that
  reviews generated scripts, executes the workflow, and exports reports

## 1. What was requested

The project was requested as a complete end-to-end mobile test automation solution with the following goals:

- Build a robust workflow for generating mobile automation scripts from screenshots
- Support dynamic input from real user-uploaded screenshots instead of a fixed sample set
- Use an agentic AI workflow where one service generates scripts and another reviews them
- Add real review and vision integration where possible
- Add Appium-based execution support
- Store generation and execution history
- Export reports in JSON and HTML formats
- Provide a usable UI and clear documentation for anyone new to the project

```
MobileTestGeneratorPOC/
├── agents/
│   ├── core/
│   │   ├── vision_agent.py         # Abstract base for vision agents
│   │   ├── testcase_agent.py       # Abstract base for test case agents
│   │   └── appium_agent.py         # Abstract base for Appium script generator agents (generate() -> {path: content})
│   ├── vision_agent.py             # OpenAIVisionAgent + MockVisionAgent + factory
│   └── __init__.py
├── models/
│   └── ssm.py                      # Single canonical Screen Semantic Model (Pydantic)
├── services/
│   ├── config.py                   # Loads .env environment variables
│   ├── pipeline.py                 # analyze_screenshot / save_semantic_model helpers
│   ├── testcase_agent.py           # OpenAITestCaseAgent + MockTestCaseAgent + factory
│   └── appium_agent.py             # OpenAIAppiumScriptAgent (LangChain self-validating POM agent) + MockAppiumScriptAgent + factory
├── pipelines/
│   ├── ssm_generator.py            # Step 1 – screenshots → SSM JSON
│   ├── testcase_generator.py       # Step 2 – SSM JSON → manual test cases
│   ├── appium_script_generator.py  # Step 3 – SSM JSON + manual test cases → Appium Page Object + test files
│   └── templates/
│       ├── appium_conftest.py      # Static driver fixture (Android), copied into artifacts/appium_scripts/ each run
│       └── appium_base_page.py     # Static BasePage (waitForVisible/click/typeText/...), copied into appium_scripts/core/ each run
```

Step 3's output layout (per screen, written under `artifacts/appium_scripts/`):

```
artifacts/appium_scripts/
├── conftest.py              # driver fixture (static)
├── core/
│   └── base_page.py         # BasePage shared helpers (static)
├── pages/
│   └── login_page.py        # LOCATORS + camelCase action methods (LLM-generated)
└── tests/
    └── test_login.py        # thin test flow using the page object only (LLM-generated)
```

## 2. What was implemented

### 2.1 Project architecture

The project is organized into the following major parts:

- Backend API built with FastAPI
- Services for vision analysis, script generation, review, and execution
- A lightweight repository layer for saving reports and history
- A Streamlit frontend for a simple user experience
- Automated tests to validate the workflow
- Report artifacts saved under the artifacts folder

### 2.2 Core workflow implemented

1. Upload one or more screenshots dynamically
2. Analyze each uploaded screen with richer, context-aware logic
3. Generate mobile automation scripts from the uploaded screen analysis
4. Review the generated scripts for quality issues
5. Execute the workflow and produce reports
6. Save and export the reports for later review

### 2.3 Backend services created

- Single-image upload and analysis endpoint
- Multi-image batch upload and analysis endpoint
- Script generation endpoint
- Batch generation endpoint for multiple screens
- Review endpoint
- Execution endpoint
- History and report retrieval endpoints

### 2.4 Review and execution capabilities

- Deterministic local review logic was implemented as a fallback
- Optional real review integration paths were added for Claude-backed analysis when credentials are available
- Appium execution support was wired in and validated at the server connectivity level
- JSON and HTML reports are generated automatically

### 2.5 User interface and reports

- A Streamlit UI was added for dynamic multi-file interaction
- The UI displays detected elements for each uploaded screen
- An optional demo mode was added so management can run a one-click sample workflow for presentations
- Report output is stored as JSON and HTML files
- The workflow can be run from the API or from a dedicated runner script

## 3. Step-by-step implementation summary

### Step 1: Project scaffolding

The repository was organized with separate folders for:

- app for API, services, repositories, schemas, and config
- agents for AI-oriented workflow components
- artifacts for reports and screenshots
- frontend for the UI
- tests for validation

### Step 2: API and service layer

A FastAPI app was created with endpoints for:

- health checks
- screenshot upload
- script generation
- review
- execution
- history and report retrieval

### Step 3: Automation generation logic

A service was implemented to transform screen analysis into Appium-style pytest scripts.

### Step 4: Review logic

A review service was implemented to analyze generated scripts for common issues such as:

- hardcoded waits
- missing explicit waits
- weak assertions
- missing logging
- lack of exception handling

### Step 5: Execution and reporting

An execution service was created to:

- run the workflow
- save a report file
- create an HTML version of the report
- record the summary and script preview

### Step 6: Persistence and history

Reports are saved to the repository so users can inspect the history and open previous runs.

### Step 7: Testing and verification

Tests were added to validate the end-to-end flow and report persistence.

## 4. How to run the project

### Prerequisites

- Python 3.11 or higher
- A virtual environment is recommended
- Optional: Appium server for real device execution
- Optional: Claude credentials for AI-backed review and vision analysis

### Step 1: Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

> Use Python 3.11 or 3.12. Python 3.15+ may not support all dependencies cleanly.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 2: Configure your `.env` file

Copy the template and fill in your values:
```bash
cp .env.example .env
```
Ask your team lead for the real `OPENAI_API_KEY` / `OPENAI_API_BASE` / `OPENAI_MODEL`
values (or your own OpenAI key), and optionally `ANTHROPIC_API_KEY` for Claude-backed review.
`.env` is gitignored - never commit it.

To run fully offline with no LLM, set all three `*_AGENT_PROVIDER` vars in `.env` to `mock`.

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Start the backend API

```bash
python main.py
```

The API will be available at:

- http://localhost:8000/docs for Swagger UI

### Step 5: Start the frontend (optional)

```bash
streamlit run frontend/app.py
```

---

## Running the Pipeline

### Step 1 – Screenshots → SSM JSON

Place your screenshots inside `artifacts/input_screenshots/`, then run:

### Step 3 – SSM JSON + Manual Test Cases → Appium Page Object Model

```powershell
python pipelines/appium_script_generator.py artifacts/ssm_json_output artifacts/manual_testcases artifacts/appium_scripts --clean
```

Output per screen: `pages/<screen>_page.py` (locators + camelCase action methods, e.g. `enterUsername`,
`tapLogin`) and `tests/test_<screen>.py` (thin test flow that only calls page-object methods — no
locators, no raw `driver` calls, no assertions-on-elements). `conftest.py` and `core/base_page.py` are
static, copied in every run, not LLM-generated. Run the generated suite with:

```powershell
python -m pytest artifacts/appium_scripts --collect-only   # sanity-check without a real Appium server
python -m pytest artifacts/appium_scripts                  # requires a running Appium server
```

Locators are best-effort placeholders derived from the SSM (`# LOCATOR_TODO` comments) — the planned
Locator Enrichment Agent resolves these to verified selectors later in the pipeline. Each page object
reserves an empty `"ios": {}` entry in its `LOCATORS` dict so iOS support can be added later without
touching any generated method.

### Full end-to-end (single command)

```powershell
python pipelines/ssm_generator.py artifacts/input_screenshots artifacts/ssm_json_output --clean ; python pipelines/testcase_generator.py artifacts/ssm_json_output artifacts/manual_testcases --clean ; python pipelines/appium_script_generator.py artifacts/ssm_json_output artifacts/manual_testcases artifacts/appium_scripts --clean
```

---

## Running Tests

```powershell
python -m unittest tests.test_ssm_model tests.test_appium_agent
```

### Step 5: Run the workflow

You can either:

- use the API endpoints, or
- run the included execution script

Example:

```bash
python run_report_flow.py
```

## 5. Execution and report output

### What happens during execution

When the workflow runs, the system:

1. accepts the input script or uploaded screen data
2. runs the generation and review pipeline
3. executes the generated workflow
4. writes a JSON report
5. writes an HTML report

### Report files generated

Current generated artifacts are stored in:

- artifacts/reports/demo_app_report.json
- artifacts/reports/demo_app_report.html

These files contain:

- app name
- execution status
- summary of the run
- script preview

## 6. Current execution status in this environment

The workflow has been run successfully in this environment and generated report artifacts.

### Verified status

- The project pipeline runs end to end
- Reports are generated and saved
- The Appium connection path was verified at the server reachability level

### Important limitation

This environment does not currently contain:

- Android SDK tools such as adb or emulator
- Android Studio AVD support
- Xcode or iOS simulator tools

Because of that, a real Android or iOS device/emulator session could not be launched from this environment.

## 7. Android and iOS emulator support

### Android emulator

A real Android emulator can be created on a machine that has:

- Android Studio installed
- Android SDK and platform tools
- hardware virtualization enabled

Typical setup steps are:

1. Install Android Studio
2. Install Android SDK and platform tools
3. Create an AVD from Device Manager
4. Start the emulator
5. Start Appium and point it to the emulator

### iOS simulator

A real iOS simulator requires:

- a macOS machine
- Xcode installed
- the iOS simulator available through Xcode

### Current environment note

This workspace does not include the required Android or iOS emulator toolchain, so real device execution is not available here yet.

## 8. Testing

Run tests with:

```bash
pytest -q
```

## 9. Summary

This project now provides a complete foundation for:

- generating mobile test scripts from screen data
- reviewing them for quality
- executing the workflow
- saving reports
- exporting reports in HTML and JSON

It is ready for further enhancement with:

- real Claude-based review and vision services
- live Appium execution against real devices
- richer UI and dashboards
- integration with CI/CD pipelines

- **Steps are loosely coupled.** Step 1 writes SSM JSON, Step 2 reads SSM JSON and writes manual test cases, Step 3 reads both and writes an Appium Page Object Model bundle. Each can run independently given its inputs on disk.
- **Providers are swappable.** Set `VISION_AGENT_PROVIDER`, `TESTCASE_AGENT_PROVIDER`, or `APPIUM_AGENT_PROVIDER` to `openai` or `mock`.
- **Single canonical model.** All screen data uses `models/ssm.py` — no duplicate schema files.
- **Prompts are externalized.** Edit `prompts/vision_analysis.txt`, `prompts/test_generation.txt`, or `prompts/appium_script_generation.txt` to tune LLM behaviour without touching code.
- **No root-level runner scripts.** Run the pipeline files in `pipelines/` directly — no wrappers needed.
- **Appium script generation (Step 3) follows Page Object Model.** For each screen the LLM generates exactly two files — a Page Object (`pages/<screen>_page.py`: locators + camelCase action methods, e.g. `enterUsername`, `tapLogin`, built on the shared `BasePage`) and a test module (`tests/test_<screen>.py`: thin, only calls page-object methods, no locators or raw driver calls). `conftest.py` and `core/base_page.py` are static templates, not LLM-generated — the model never has to reinvent driver setup or wait boilerplate.
- **Self-validating generation loop.** `OpenAIAppiumScriptAgent` uses `ChatOpenAI.bind_tools()` (not `langchain.agents.AgentExecutor` — its internal streaming call was incompatible with some OpenAI-compatible gateways on larger payloads) in a manual tool-calling loop: the model drafts both files, calls `validate_pom_files` on its own draft, and retries (capped) until clean. That tool checks Python syntax (`ast.parse`), Appium anti-patterns (`time.sleep`, fragile `//*` XPath, deprecated `find_element_by_*`), **and** cross-file consistency — every page-object method the test file calls must actually be defined on the page object, since an `AttributeError` from a name mismatch only surfaces at test *execution* time and `pytest --collect-only` doesn't catch it. `MockAppiumScriptAgent` builds the same POM shape deterministically from the SSM, offline, for demos/CI.
- **Locators are placeholders pending enrichment.** Generated page objects use SSM label/accessibility-id best guesses tagged `# LOCATOR_TODO`; the planned Locator Enrichment Agent resolves real, verified selectors later in the pipeline. Reviewer and Execution agents are also still planned.
- **Android only for now, iOS door left open.** `conftest.py` raises `NotImplementedError` for `MOBILE_PLATFORM=ios`, and every generated `LOCATORS` dict reserves an empty `"ios": {}` entry — adding iOS later is additive (populate locators + implement `XCUITestOptions`), not a rewrite of any generated page object or test.
