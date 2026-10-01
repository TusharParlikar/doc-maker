"""Consistency checks for skills/*/SKILL.md. Run: python tests/test_skills.py"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = {p.parent.name: p for p in ROOT.glob("skills/*/SKILL.md")}
PREFIX = {"doc-maker": "D", "database-docs": "DB", "architecture-docs": "A"}


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert m, "missing frontmatter"
    return dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M))


def defined_rules():
    rules = {}
    for name, path in SKILLS.items():
        ids = re.findall(r"^\*\*(D|DB|A)(\d+)\. ", path.read_text(encoding="utf-8"), re.M)
        rules[name] = [p + n for p, n in ids]
    return rules


def test_frontmatter():
    assert set(SKILLS) == set(PREFIX), SKILLS
    for name, path in SKILLS.items():
        fm = frontmatter(path.read_text(encoding="utf-8"))
        assert fm["name"] == name, (name, fm["name"])
        assert re.fullmatch(r"[a-z0-9-]{1,64}", fm["name"])
        assert 50 < len(fm["description"]) <= 1024, (name, len(fm["description"]))


def test_rules_numbered_and_tiered():
    for name, ids in defined_rules().items():
        p = PREFIX[name]
        assert ids and all(i.startswith(p) and i[len(p):].isdigit() for i in ids), (name, ids)
        nums = [int(i[len(p):]) for i in ids]
        assert nums == list(range(1, len(nums) + 1)), (name, nums)
        text = SKILLS[name].read_text(encoding="utf-8")
        for block in re.split(r"\n(?=\*\*(?:D|DB|A)\d+\. )", text)[1:]:
            head = block.splitlines()[0]
            assert "Tier" in head or "always" in head or "applies whenever" in head, head
            if "applies whenever" not in head and "always" not in head.split("·")[-1]:
                assert "Look for:" in block and "Output:" in block, head


def test_cross_references_resolve():
    all_ids = {i for ids in defined_rules().values() for i in ids}
    for name, path in SKILLS.items():
        text = path.read_text(encoding="utf-8")
        for ref in set(re.findall(r"\b((?:DB|D|A)\d+)\b", text)):
            assert ref in all_ids, f"{name}: reference {ref} has no rule"
        for lo, hi in re.findall(r"\b((?:DB|D|A)\d+)-((?:DB|D|A)\d+)\b", text):
            assert lo in all_ids and hi in all_ids, f"{name}: range {lo}-{hi}"
            pre = re.match(r"[A-Z]+", hi).group(0)
            last = max(int(i[len(pre):]) for i in all_ids if re.fullmatch(pre + r"\d+", i))
            assert int(hi[len(pre):]) == last, f"{name}: range {lo}-{hi} but last rule is {pre}{last}"


def test_referenced_files_exist():
    for name, path in SKILLS.items():
        text = path.read_text(encoding="utf-8")
        for f in set(re.findall(r"`(?:references/)?([\w-]+-templates?\.md)`", text)):
            assert (path.parent / "references" / f).exists(), f"{name}: missing references/{f}"
        if "evidence.py" in text:
            assert (path.parent / "scripts" / "evidence.py").exists(), f"{name}: missing scripts/evidence.py"


def test_changelog_maps_every_old_rule():
    """CHANGELOG maps each 1.x rule (1-85) exactly once, to IDs that exist in 2.0."""
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    table = text.split("### Rule mapping")[1].split("\n## ")[0]
    all_ids = {i for ids in defined_rules().values() for i in ids}
    seen = {}
    for row in re.findall(r"^\|.*\|$", table, re.M):
        cells = [c.strip() for c in row.strip("|").split("|")]
        for old, new in zip(cells[0::2], cells[1::2]):
            if old.isdigit():
                assert old not in seen, f"rule {old} mapped twice"
                seen[old] = new
                for ref in re.findall(r"\b(?:DB|D|A)\d+\b", new):
                    assert ref in all_ids, f"old rule {old} maps to missing {ref}"
                assert re.search(r"\b(?:DB|D|A)\d+\b|Process|Standards", new), (old, new)
    assert sorted(map(int, seen)) == list(range(1, 86)), sorted(map(int, seen))


if __name__ == "__main__":
    for t in (test_frontmatter, test_rules_numbered_and_tiered, test_cross_references_resolve,
              test_referenced_files_exist, test_changelog_maps_every_old_rule):
        t()
    counts = {k: len(v) for k, v in defined_rules().items()}
    print(f"ok: skills consistent {counts} = {sum(counts.values())} rules")
