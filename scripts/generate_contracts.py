"""Write (or with --check, verify) the OpenAPI snapshot in contracts/.

The snapshot is committed so an API change shows up as a diff in review,
next to the spec change that asked for it.
"""

import json
import sys
from pathlib import Path

from library.app import create_app

TARGET = Path(__file__).resolve().parent.parent / "contracts" / "openapi.json"
current = json.dumps(create_app().openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"

if "--check" in sys.argv:
    if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != current:
        print("contracts/openapi.json is stale — run `make contracts-update` and commit it.")
        sys.exit(1)
    print("contracts: ok")
else:
    TARGET.write_text(current, encoding="utf-8")
    print(f"wrote {TARGET.name}")
