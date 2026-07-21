"""Populate artifacts/locator_output/*.json with real locators grounded in a live
Appium session, replacing agents/locator_agent.py's hardcoded per-app dictionary.

For each SSM file: connects once to Appium, navigates to the screen using
artifacts/navigation_output/navigation_map.json, dumps the live page_source, and
asks the Locator Agent to match SSM elements to real UI nodes from that dump.

Usage: python pipelines/locator_generator.py <ssm-folder> [--provider mock|openai]
Requires an Appium server + emulator already running (same env vars as
pipelines/appium_script_generator.py: APPIUM_SERVER_URL, ANDROID_APP_PATH,
ANDROID_DEVICE_NAME).
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.config import load_environment
from services.appium_agent import load_navigation_map, load_navigation_steps
from services.appium_runtime import navigate, open_session, reset_to_home
from services.live_locator_agent import create_live_locator_agent

load_environment()

OUTPUT_DIR = ROOT / "artifacts" / "locator_output"


def _slugify(screen_name: str) -> str:
    import re

    return re.sub(r"[^A-Za-z0-9]+", "_", screen_name.strip()).strip("_") or "Screen"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("Usage: python pipelines/locator_generator.py <ssm-folder> [--provider mock|openai]")
        return 2

    ssm_folder = Path(args[0])
    provider = None
    if "--provider" in args:
        provider = args[args.index("--provider") + 1]

    if not ssm_folder.exists() or not ssm_folder.is_dir():
        print(f"SSM input path must be an existing folder: {ssm_folder}")
        return 2

    ssm_files = sorted(p for p in ssm_folder.iterdir() if p.suffix.lower() == ".json")
    if not ssm_files:
        print(f"No SSM JSON files found in {ssm_folder}")
        return 2

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    navigation_map = load_navigation_map()
    agent = create_live_locator_agent(provider=provider)

    print(f"Connecting to Appium session for {len(ssm_files)} screen(s)...")
    driver = open_session()
    try:
        for ssm_file in ssm_files:
            ssm_data = json.loads(ssm_file.read_text(encoding="utf-8"))
            screen_name = ssm_data.get("screen_name") or ssm_file.stem

            try:
                reset_to_home(driver)
                steps = load_navigation_steps(screen_name, navigation_map)
                navigate(driver, steps)
                # Give the screen a moment to finish rendering after the last nav tap -
                # page_source can otherwise be captured mid-transition, missing the
                # very elements we need to ground (this emulator is software-rendered
                # and slow enough for that race to matter).
                time.sleep(1.5)
                page_source = driver.page_source

                locator_payload = agent.resolve(ssm_data, page_source)
                out_path = OUTPUT_DIR / f"locator_{_slugify(screen_name)}.json"
                out_path.write_text(json.dumps(locator_payload, indent=2) + "\n", encoding="utf-8")
                print(f"Wrote {out_path} ({len(locator_payload['elements'])}/{len(ssm_data.get('elements') or [])} SSM elements grounded)")
            except Exception as exc:
                print(f"FAILED {screen_name}: {exc}")
    finally:
        driver.quit()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
