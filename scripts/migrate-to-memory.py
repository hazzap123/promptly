#!/usr/bin/env python3
"""
One-time migration: import prompts from YAML library into ChromaDB memory.
Run once. Safe to re-run (deduplication via content hash in store_memory).
"""
import sys
from pathlib import Path

OLLAMA_DIR = Path.home() / "github" / "ea" / ".ollama"
LIBRARY_PATH = Path.home() / "github" / "ea" / "00-system" / "prompt-library.yaml"

sys.path.insert(0, str(OLLAMA_DIR))

try:
    import yaml
except ImportError:
    print("Install pyyaml: pip install pyyaml")
    sys.exit(1)

from memory import remember_prompt


def main():
    if not LIBRARY_PATH.exists():
        print(f"Library not found at {LIBRARY_PATH}")
        return

    with open(LIBRARY_PATH) as f:
        data = yaml.safe_load(f)

    prompts = data.get("prompts", []) if data else []
    if not prompts:
        print("No prompts to migrate.")
        return

    print(f"Migrating {len(prompts)} prompts...")
    success = 0
    for p in prompts:
        name = p.get("id", "unknown")
        prompt_text = p.get("prompt", "")
        triggers = p.get("triggers", [])
        if not name or not prompt_text or not triggers:
            print(f"  - Skipping '{name}': missing required fields")
            continue
        result = remember_prompt(name, prompt_text, triggers)
        print(f"  + {name}: {result[:70]}")
        success += 1

    print(f"\nDone. {success}/{len(prompts)} prompts written to memory.")


if __name__ == "__main__":
    main()
