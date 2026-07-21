import json
import os
import shutil
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.config import load_environment
from services.appium_agent import create_appium_agent, load_locator_data, load_navigation_map, load_navigation_steps

load_environment()

CONFTEST_TEMPLATE = ROOT / "pipelines" / "templates" / "appium_conftest.py"
BASE_PAGE_TEMPLATE = ROOT / "pipelines" / "templates" / "appium_base_page.py"


def _find_matching_testcase_file(ssm_file: Path, testcase_files: list[Path]) -> Optional[Path]:
    prefix = f"manual_testcases_{ssm_file.stem}"
    for candidate in testcase_files:
        if candidate.stem.startswith(prefix):
            return candidate
    return None


def _copy_static_templates(out_dir_path: Path) -> None:
    if CONFTEST_TEMPLATE.exists():
        shutil.copyfile(CONFTEST_TEMPLATE, out_dir_path / "conftest.py")
    else:
        print(f"WARNING: conftest template not found at {CONFTEST_TEMPLATE}; generated scripts will have no driver fixture.")

    core_dir = out_dir_path / "core"
    core_dir.mkdir(parents=True, exist_ok=True)
    if BASE_PAGE_TEMPLATE.exists():
        shutil.copyfile(BASE_PAGE_TEMPLATE, core_dir / "base_page.py")
    else:
        print(f"WARNING: base_page template not found at {BASE_PAGE_TEMPLATE}; generated page objects will fail to import.")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 2:
        print("Usage: python pipelines/appium_script_generator.py <ssm-folder> <testcases-folder> [output-dir] --clean")
        return 2

    ssm_folder = Path(args[0])
    testcases_folder = Path(args[1])
    out = args[2] if len(args) > 2 and not args[2].startswith("--") else "artifacts/appium_scripts"
    clean = "--clean" in args

    if not ssm_folder.exists() or not ssm_folder.is_dir():
        print(f"SSM input path must be an existing folder: {ssm_folder}")
        return 2
    if not testcases_folder.exists() or not testcases_folder.is_dir():
        print(f"Test case input path must be an existing folder: {testcases_folder}")
        return 2

    ssm_files = sorted(p for p in ssm_folder.iterdir() if p.suffix.lower() == ".json")
    if not ssm_files:
        print(f"No SSM JSON files found in {ssm_folder}")
        return 2

    testcase_files = sorted(p for p in testcases_folder.iterdir() if p.suffix.lower() == ".txt")
    navigation_map = load_navigation_map()

    out_dir_path = Path(out)
    if clean and out_dir_path.exists():
        shutil.rmtree(out_dir_path)
    out_dir_path.mkdir(parents=True, exist_ok=True)

    _copy_static_templates(out_dir_path)

    provider = os.getenv("APPIUM_AGENT_PROVIDER") or ("openai" if os.getenv("OPENAI_API_KEY") else "mock")
    prompt_path = ROOT / "prompts" / "appium_script_generation.txt"
    prompt_template = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else None
    agent = create_appium_agent(provider=provider, prompt_template=prompt_template)

    print(f"Found {len(ssm_files)} SSM files. Generating Appium Page Object + test bundles...")
    for ssm_file in ssm_files:
        testcase_file = _find_matching_testcase_file(ssm_file, testcase_files)
        if testcase_file is None:
            print(f"SKIPPED {ssm_file}: no matching manual test case file found in {testcases_folder}")
            continue

        try:
            ssm_data = json.loads(ssm_file.read_text(encoding="utf-8"))
            testcases_text = testcase_file.read_text(encoding="utf-8")

            screen_name = ssm_data.get("screen_name") or ssm_file.stem
            locator_data = load_locator_data(screen_name)
            if locator_data is not None:
                print(f"Using resolved locators for {screen_name}")
            else:
                print(f"No locator file found for {screen_name}; falling back to guessed locators.")

            navigation_steps = load_navigation_steps(screen_name, navigation_map)
            if navigation_steps:
                print(f"Using navigation steps for {screen_name}: {len(navigation_steps)} step(s)")

            files = agent.generate(
                ssm_data,
                testcases_text,
                filename=ssm_file.stem,
                locator_data=locator_data,
                navigation_steps=navigation_steps,
            )

            for relative_path, content in files.items():
                out_path = out_dir_path / relative_path
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(content, encoding="utf-8")
                print(f"Wrote {out_path}")
        except Exception as exc:
            print(f"FAILED {ssm_file}: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
