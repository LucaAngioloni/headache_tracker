#!/usr/bin/env python3
"""Bump the app version in frontend/package.json and backend settings in sync."""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {pathlib.Path(__file__).name} <version>")
    version = sys.argv[1]

    package_json = ROOT / "frontend" / "package.json"
    data = json.loads(package_json.read_text())
    data["version"] = version
    package_json.write_text(json.dumps(data, indent=2) + "\n")

    settings_path = ROOT / "backend" / "config" / "settings" / "base.py"
    src = re.sub(
        r'(^VERSION = ")[^"]*(")',
        rf"\g<1>{version}\g<2>",
        settings_path.read_text(),
        count=1,
        flags=re.M,
    )
    settings_path.write_text(src)

    print(f"Version bumped to {version} (frontend/package.json and backend settings).")


if __name__ == "__main__":
    main()
