"""Audit Lab 2–4 without changing them; write evidence only inside Lab6/evidence."""

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "Lab6/evidence"


def main():
    before = json.loads((EVIDENCE / "protected-files-before.json").read_text())
    after = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in before}
    assert before == after, "A protected Lab 2–4 file changed"
    subprocess.run(
        ["git", "diff", "--exit-code", "ee8aacbb910ecee079c9c9b4cf17305b99a6e1f3", "--", *before],
        cwd=ROOT, check=True, capture_output=True,
    )
    (EVIDENCE / "protected-files-after.json").write_text(json.dumps(after, indent=2) + "\n")

    lab3 = (ROOT / "Lab3/Lab3.md").read_text()
    section = lab3.split("## 7. Шинэчилсэн Product Backlog")[1].split("## 8.")[0]
    points = {}
    for row in section.splitlines():
        cells = [cell.strip().strip("*") for cell in row.split("|")[1:-1]]
        if cells and re.fullmatch(r"US-\d+", cells[0]):
            points[cells[0]] = int(cells[4])
    assert len(points) == 15
    sprint = sum(points[f"US-{i:02}"] for i in range(1, 9))

    lab4 = (ROOT / "Lab4/README.MD4.txt").read_text()
    section = lab4.split("## 5. Симуляцийн өгөгдөл")[1].split("## 6.")[0]
    cards = [(m[0], *map(int, m[1:])) for m in re.findall(
        r"\| (US-\d+) \| (\d+) \| (\d+) \| (\d+) \|", section
    )]
    assert len(cards) == 8
    section = lab4.split("### 10.1. CFD хүснэгт")[1].split("### 10.2.")[0]
    original = [[int(value) for value in match] for match in re.findall(
        r"\| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|", section
    )]
    comparison = []
    for day, *values in original:
        expected = [
            sum(day < start for _, start, review, done in cards),
            sum(start <= day < review for _, start, review, done in cards),
            sum(review <= day < done for _, start, review, done in cards),
            sum(done <= day for _, start, review, done in cards),
        ]
        assert sum(expected) == 8
        comparison.append({"day": day, "original": values, "recomputed": expected, "matches": values == expected})
    cycle_sum = sum(done - start for _, start, review, done in cards)
    result = {
        "protected_files_unchanged": True,
        "product_backlog_sp": sum(points.values()),
        "sprint_backlog_sp": sprint,
        "remaining_sp": sum(points.values()) - sprint,
        "capacity_formula_unit": "36 person-hours, not automatically 36 story points",
        "cycle_time_sum": cycle_sum,
        "cycle_time_average": cycle_sum / len(cards),
        "day_end_convention": "start <= day < review; review <= day < done; done <= day",
        "cfd_comparison": comparison,
    }
    (EVIDENCE / "lab2-4-numeric-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("PASS: protected Lab 2–4 bytes and git diff are unchanged")
    print(f"Backlog: {sum(points.values())} SP; Sprint: {sprint} SP; remaining: {sum(points.values())-sprint} SP")
    print(f"Cycle Time: {cycle_sum} / {len(cards)} = {cycle_sum/len(cards)} days")
    print("CFD mismatch days:", [row["day"] for row in comparison if not row["matches"]])


if __name__ == "__main__":
    main()
