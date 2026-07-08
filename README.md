# Mobile Test Generator POC

A two-step pipeline that turns mobile app screenshots into manual test cases using a vision-capable LLM.

---

## Project Structure

```
MobileTestGeneratorPOC/
├── agents/
│   ├── core/
│   │   ├── vision_agent.py         # Abstract base for vision agents
│   │   └── testcase_agent.py       # Abstract base for test case agents
│   ├── vision_agent.py             # OpenAIVisionAgent + MockVisionAgent + factory
│   └── __init__.py
├── models/
│   └── ssm.py                      # Single canonical Screen Semantic Model (Pydantic)
├── services/
│   ├── config.py                   # Loads .env environment variables
│   ├── pipeline.py                 # analyze_screenshot / save_semantic_model helpers
│   └── testcase_agent.py           # OpenAITestCaseAgent + MockTestCaseAgent + factory
├── pipelines/
│   ├── ssm_generator.py            # Step 1 – screenshots → SSM JSON
│   └── testcase_generator.py       # Step 2 – SSM JSON → manual test cases
```

---

## Setup

### 1. Create a virtual environment

**Windows PowerShell:**
```powershell
cd C:\Users\priyanka.pattewar\MobileTestGeneratorPOC
.\scripts\setup_env.ps1 -PythonExe python
```

**macOS / Linux:**
```bash
cd /path/to/MobileTestGeneratorPOC
bash scripts/setup_env.sh
```

> Use Python 3.11 or 3.12. Python 3.15+ may not support all dependencies cleanly.

### 2. Configure your `.env` file

```dotenv
VISION_AGENT_PROVIDER=openai
TESTCASE_AGENT_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_BASE=https://api.openai.com/v1   # Optional – override for custom gateways
```

To test without an API key, set both providers to `mock`:
```dotenv
VISION_AGENT_PROVIDER=mock
TESTCASE_AGENT_PROVIDER=mock
```

---

## Running the Pipeline

### Step 1 – Screenshots → SSM JSON

Place your screenshots inside `artifacts/input_screenshots/`, then run:

```powershell
python pipelines/ssm_generator.py artifacts/input_screenshots artifacts/ssm_json_output --clean
```

Output: one `ssm_<ScreenName>_<timestamp>.json` file per screenshot in `artifacts/ssm_json_output/`.

### Step 2 – SSM JSON → Manual Test Cases

```powershell
python pipelines/testcase_generator.py artifacts/ssm_json_output artifacts/manual_testcases --clean
```

Output: one `manual_testcases_<name>_<timestamp>.txt` file per SSM JSON in `artifacts/manual_testcases/`.

### Full end-to-end (single command)

```powershell
python pipelines/ssm_generator.py artifacts/input_screenshots artifacts/ssm_json_output --clean ; python pipelines/testcase_generator.py artifacts/ssm_json_output artifacts/manual_testcases --clean
```

---

## Supported Image Formats

`png`, `jpg`, `jpeg`, `webp`, `bmp`

---

## Running Tests

```powershell
python -m unittest tests.test_ssm_model
```

---

## Architecture Notes

- **Step 1 and Step 2 are loosely coupled.** Step 1 writes SSM JSON; Step 2 reads it. They can run independently.
- **Providers are swappable.** Set `VISION_AGENT_PROVIDER` or `TESTCASE_AGENT_PROVIDER` to `openai` or `mock`.
- **Single canonical model.** All screen data uses `models/ssm.py` — no duplicate schema files.
- **Prompts are externalized.** Edit `prompts/vision_analysis.txt` or `prompts/test_generation.txt` to tune LLM behaviour without touching code.
- **No root-level runner scripts.** Run the pipeline files in `pipelines/` directly — no wrappers needed.
- **Appium script generation** is planned as a future step and is not yet implemented.
