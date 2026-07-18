#!/usr/bin/env python3
"""Pre-publish secret scan. Patterns are composed at runtime so this file
never contains them literally (avoids self-matching false positives)."""
import os, sys

PATTERNS = ["github_" + "pat_", "AIza" + "Sy", "AQ." + "Ab8", "spsolanki"]
SKIP_DIRS = {".git", "__pycache__"}
found = False
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in files:
        if f == "scan.py":
            continue
        p = os.path.join(root, f)
        if f == ".env":
            print(f"!!! {p} — .env file must never be committed"); found = True; continue
        try:
            text = open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for pat in PATTERNS:
            if pat in text:
                print(f"!!! {p} contains '{pat[:6]}…'"); found = True
print("SECRET FOUND — DO NOT PUBLISH" if found else "clean — no secrets")
sys.exit(1 if found else 0)
