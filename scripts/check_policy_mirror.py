"""`make mirror`: the code's policy must be byte-identical to the spec's (ADR-0003)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "specs" / "policy.yaml"
CODE = ROOT / "src" / "library" / "lending" / "domain" / "policy.yaml"

if SPEC.read_bytes() != CODE.read_bytes():
    print(f"policy drift: {CODE.relative_to(ROOT)} differs from {SPEC.relative_to(ROOT)}")
    print("The spec owns the numbers: change specs/policy.yaml, then copy it over.")
    sys.exit(1)
print("policy mirror: ok")
