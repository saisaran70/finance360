"""
Auto-updates the Obsidian vault's frontmatter dates when Claude Code stops.
Runs via the Stop hook in .claude/settings.json.
"""
import os
import re
from datetime import date

VAULT = os.path.join(os.path.dirname(__file__), "..", "obsidian")
TODAY = date.today().isoformat()

DATE_RE = re.compile(r"^(updated:\s*)(.+)$", re.MULTILINE)

TRACKED = [
    "home.md",
    "decisions.md",
    "progress.md",
    "roadmap.md",
]


def update_date(path):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    updated = DATE_RE.sub(lambda m: m.group(1) + TODAY, content)
    if updated != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"  updated: {os.path.basename(path)}")


def main():
    print(f"[obsidian] Updating vault timestamps → {TODAY}")
    for filename in TRACKED:
        update_date(os.path.join(VAULT, filename))
    print("[obsidian] Done.")


if __name__ == "__main__":
    main()
