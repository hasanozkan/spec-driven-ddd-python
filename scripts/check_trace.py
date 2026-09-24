"""`make trace`: spec rules and tests must point at each other.

Every rule id written in a feature spec (`**LEND-R3**`) needs at least one
test tagged `@pytest.mark.rule("LEND-R3")`; every tag must name a rule that
exists. A rule nobody proves, or a test proving a rule nobody wrote, fails.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULE_IN_SPEC = re.compile(r"\*\*([A-Z]+-R\d+)\*\*")
RULE_IN_TEST = re.compile(r"""mark\.rule\(\s*["']([A-Z]+-R\d+)["']\s*\)""")

spec_rules = {
    rule: path.relative_to(ROOT)
    for path in sorted((ROOT / "specs" / "features").glob("*/README.md"))
    for rule in RULE_IN_SPEC.findall(path.read_text(encoding="utf-8"))
}
tested = {
    rule
    for path in (ROOT / "tests").rglob("test_*.py")
    for rule in RULE_IN_TEST.findall(path.read_text(encoding="utf-8"))
}

untested = sorted(set(spec_rules) - tested)
unknown = sorted(tested - set(spec_rules))
for rule in untested:
    print(f"untested rule: {rule} ({spec_rules[rule]})")
for rule in unknown:
    print(f"test cites a rule no spec defines: {rule}")
if untested or unknown:
    sys.exit(1)
print(f"trace: ok — {len(spec_rules)} rules, each proven by a test")
