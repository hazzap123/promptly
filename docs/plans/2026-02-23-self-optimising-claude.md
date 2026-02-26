# Self-Optimising Claude Interaction Layer — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a system where Claude proactively intercepts weak prompts, surfaces saved patterns, writes prompt learnings to memory, and autonomously suggests automations — without waiting to be asked.

**Architecture:** Five components wired together: (1) `prompt` and `automation-candidate` types added to ChromaDB memory, (2) a prompt-intercept hook on every UserPromptSubmit that injects matches, (3) session-context.sh enhanced to surface optimisation suggestions, (4) promptly.md enhanced to write to memory and track outcomes, (5) ~/CLAUDE.md proactive section rewritten for active coaching.

**Tech Stack:** Python 3, ChromaDB, Ollama (nomic-embed-text + llama3.2:3b), Claude Code hooks (bash/python), YAML, Markdown skill files.

---

## Task 1: Add `prompt` and `automation-candidate` memory types

**Files:**
- Modify: `/Users/harryparkes/github/ea/.ollama/config.py` (MEMORY_TYPES list)
- Modify: `/Users/harryparkes/github/ea/.ollama/memory.py` (add helpers)

**Step 1: Add types to config.py**

In `config.py`, find the MEMORY_TYPES list and add two new types:

```python
MEMORY_TYPES = [
    "decision",
    "preference",
    "person",
    "project",
    "commitment",
    "lesson",
    "context",
    "prompt",                 # ← add
    "automation-candidate",   # ← add
]
```

**Step 2: Add helper functions to memory.py**

At the end of memory.py, before any `if __name__ == "__main__"` block, add:

```python
def remember_prompt(name: str, prompt_text: str, triggers: list[str]) -> str:
    """Store a reusable prompt pattern in memory."""
    content = f"PROMPT:{name} | TRIGGERS:{','.join(triggers)} | {prompt_text[:500]}"
    return remember(content, "prompt")


def remember_automation_candidate(description: str, frequency: int = 1) -> str:
    """Store a repeated manual action that could be automated."""
    content = f"CANDIDATE(x{frequency}): {description}"
    return remember(content, "automation-candidate")
```

**Step 3: Verify the types are accepted**

```bash
python3 -c "
import sys; sys.path.insert(0, '/Users/harryparkes/github/ea/.ollama')
from config import MEMORY_TYPES
assert 'prompt' in MEMORY_TYPES, 'prompt type missing'
assert 'automation-candidate' in MEMORY_TYPES, 'automation-candidate type missing'
print('OK:', MEMORY_TYPES)
"
```

Expected: `OK: [...]` with both new types present.

**Step 4: Test remember_prompt**

```bash
python3 -c "
import sys; sys.path.insert(0, '/Users/harryparkes/github/ea/.ollama')
from memory import remember_prompt
result = remember_prompt('test-prompt', 'Analyze [TOPIC] using TAM/SAM/SOM', ['market size', 'TAM'])
print(result)
"
```

Expected: `Remembered (stored): PROMPT:test-prompt...`

**Step 5: Commit**

```bash
cd /Users/harryparkes/github/ea
git add .ollama/config.py .ollama/memory.py
git commit -m "feat: add prompt and automation-candidate memory types"
```

---

## Task 2: Write prompt-intercept.py hook

**Files:**
- Create: `~/.claude/hooks/prompt-intercept.py`
- Modify: `~/.claude/settings.json`

**Step 1: Create the hook script**

Create `/Users/harryparkes/.claude/hooks/prompt-intercept.py`:

```python
#!/usr/bin/env python3
"""
UserPromptSubmit hook: intercepts incoming prompts and checks for saved patterns.

Two behaviours:
1. Match: if prompt semantically matches a stored 'prompt' type memory, inject it
2. Candidate: if prompt is very short (<15 words) for what looks like a complex ask, note it

Silent failure — never blocks the user. Under 200ms target.
"""
import json
import sys
import time
from pathlib import Path

OLLAMA_DIR = Path.home() / "github" / "ea" / ".ollama"
MATCH_THRESHOLD = 0.35  # Distance threshold for prompt match (lower = stricter)
MIN_PROMPT_WORDS = 5    # Skip trivially short prompts

def main():
    raw = sys.stdin.read().strip()
    if not raw:
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return

    prompt = data.get("user_prompt", "").strip()
    if not prompt or len(prompt.split()) < MIN_PROMPT_WORDS:
        return

    # Skip commands (start with /)
    if prompt.startswith("/"):
        return

    sys.path.insert(0, str(OLLAMA_DIR))
    try:
        from utils import get_embedding, get_chroma_client, get_collection
        from config import CHROMA_PATH, MEMORY_COLLECTION
    except ImportError:
        return

    try:
        start = time.time()
        embedding = get_embedding(prompt[:500])
        client = get_chroma_client(CHROMA_PATH)
        collection = get_collection(client, MEMORY_COLLECTION)

        results = collection.query(
            query_embeddings=[embedding],
            n_results=3,
            where={"type": "prompt"},
            include=["documents", "metadatas", "distances"],
        )

        if not results["documents"] or not results["documents"][0]:
            return

        matches = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            if dist <= MATCH_THRESHOLD:
                # Extract name from "PROMPT:name | TRIGGERS:... | ..."
                name = doc.split("|")[0].replace("PROMPT:", "").strip() if doc.startswith("PROMPT:") else "saved prompt"
                matches.append((name, dist))

        if not matches:
            return

        elapsed = int((time.time() - start) * 1000)
        if elapsed > 500:  # Too slow, bail silently
            return

        top_name, top_dist = matches[0]
        context = f"[Promptly] Your library has a refined version of this: '{top_name}'. Run `/promptly match` to use it, or proceed as-is."
        print(json.dumps({"additionalContext": context}))

    except Exception:
        return


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
```

**Step 2: Make it executable**

```bash
chmod +x /Users/harryparkes/.claude/hooks/prompt-intercept.py
```

**Step 3: Wire to UserPromptSubmit in settings.json**

In `/Users/harryparkes/.claude/settings.json`, add to the `UserPromptSubmit.hooks` array (alongside the existing enrich.py entry):

```json
{
  "type": "command",
  "command": "python3 ~/.claude/hooks/prompt-intercept.py",
  "timeout": 3
}
```

The full UserPromptSubmit section becomes:

```json
"UserPromptSubmit": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 ~/github/ea/.claude/hooks/enrich.py",
        "timeout": 3
      },
      {
        "type": "command",
        "command": "python3 ~/.claude/hooks/prompt-intercept.py",
        "timeout": 3
      },
      {
        "type": "command",
        "command": "date '+Current time: %A %d %b %Y, %H:%M %Z'",
        "timeout": 2
      },
      {
        "type": "command",
        "command": "python3 ~/.claude/hooks/calendar-sync.py",
        "timeout": 5
      }
    ]
  }
]
```

**Step 4: Test the hook manually**

```bash
echo '{"user_prompt": "analyze market opportunity for eldercare tech", "session_id": "test"}' \
  | python3 ~/.claude/hooks/prompt-intercept.py
```

Expected: Either empty output (no match yet) or `{"additionalContext": "..."}` if a matching prompt exists.

**Step 5: Commit**

```bash
cd /Users/harryparkes/.claude
git add hooks/prompt-intercept.py
# settings.json is not in a git repo — no commit needed
```

---

## Task 3: Enhance session-context.sh with optimisation surface

**Files:**
- Modify: `/Users/harryparkes/.claude/hooks/session-context.sh`

**Step 1: Add optimisation recall section at the end of session-context.sh**

Find the `# --- Output ---` section at the bottom of session-context.sh and insert the following block immediately before it:

```bash
# --- 4. Optimisation suggestions (automation candidates + high-frequency prompts) ---
OPT_OUTPUT=""
if [ -d "$MEM_MODULE" ]; then
    OPT_OUTPUT=$(python3 -c "
import sys
sys.path.insert(0, '$MEM_MODULE')
try:
    from utils import get_embedding, get_chroma_client, get_collection
    from config import CHROMA_PATH, MEMORY_COLLECTION

    client = get_chroma_client(CHROMA_PATH)
    collection = get_collection(client, MEMORY_COLLECTION)

    # Get all automation-candidate memories
    results = collection.get(
        where={'type': 'automation-candidate'},
        include=['documents', 'metadatas']
    )

    candidates = []
    if results and results.get('documents'):
        for doc in results['documents']:
            candidates.append(doc)

    if candidates:
        print('**Optimisation opportunities:**')
        for c in candidates[:3]:
            print(f'- {c}')
except Exception:
    pass
" 2>/dev/null)
fi

if [ -n "$OPT_OUTPUT" ]; then
    OUTPUT+="\n${OPT_OUTPUT}\n"
fi
```

**Step 2: Test session-context.sh runs without error**

```bash
bash ~/.claude/hooks/session-context.sh
```

Expected: Same output as before (optimisation section empty until candidates accumulate), no errors.

**Step 3: Commit**

session-context.sh is in `~/.claude/hooks/` — verify if tracked by git, then commit if so.

```bash
cd ~/.claude && git status hooks/session-context.sh 2>/dev/null || echo "not in git"
```

---

## Task 4: Enhance promptly.md to write to memory

**Files:**
- Modify: `/Users/harryparkes/.claude/commands/promptly.md`
- Modify: `/Users/harryparkes/github/promptly/promptly.md` (source of truth)

This is a text edit to the skill file — no tests applicable.

**Step 1: Add MCP memory tools to allowed-tools in both promptly.md files**

Find the `allowed-tools:` block:

```yaml
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
```

Replace with:

```yaml
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
  - mcp__memory__memory_remember
  - mcp__memory__memory_recall
```

**Step 2: Add memory write step to Phase 3 (Add to Library)**

In the `## Mode: Distill` section, after step 6 "Write to library" (the YAML write step), add:

```markdown
7. **Write to memory layer:**
   - Call `mcp__memory__memory_remember` with:
     - content: `PROMPT:{id} | TRIGGERS:{triggers joined} | {first 400 chars of prompt}`
     - type: `prompt`
   - This enables cross-session semantic recall via the intercept hook
   - Confirm: "Saved to memory layer."
```

**Step 3: Add outcome tracking step to proactive detection**

In `<proactive_detection>`, after "If yes: Proceed to Distill mode", add:

```markdown
**Silent outcome tracking (always-on):**
When Harry expresses satisfaction ("perfect", "yes that's it", "exactly", "great") after multiple
iterations on any topic — even if /promptly is declined — call `mcp__memory__memory_remember` with:
- content: `CANDIDATE: [one-line description of the pattern] (satisfaction confirmed)`
- type: `automation-candidate`

This feeds the session-start optimisation surface without interrupting the conversation.
```

**Step 4: Sync edit to the commands version**

```bash
cp /Users/harryparkes/github/promptly/promptly.md /Users/harryparkes/.claude/commands/promptly.md
```

**Step 5: Verify the YAML is still valid**

```bash
python3 -c "
import re
with open('/Users/harryparkes/.claude/commands/promptly.md') as f:
    content = f.read()
# Check allowed-tools contains new entries
assert 'mcp__memory__memory_remember' in content, 'memory_remember missing'
assert 'mcp__memory__memory_recall' in content, 'memory_recall missing'
print('OK')
"
```

**Step 6: Commit**

```bash
cd /Users/harryparkes/github/promptly
git add promptly.md
git commit -m "feat: write prompt patterns to memory layer on distill"
```

---

## Task 5: Rewrite proactive coaching section in ~/CLAUDE.md

**Files:**
- Modify: `/Users/harryparkes/CLAUDE.md`

**Step 1: Read the current proactive section**

Read the section between `<!-- promptly:proactive-start -->` and `<!-- promptly:proactive-end -->` in `/Users/harryparkes/CLAUDE.md`.

**Step 2: Replace the proactive section**

Replace the content between the markers (keeping the markers themselves) with:

```markdown
<!-- promptly:proactive-start -->
## Active Coaching & Self-Optimisation

Claude operates as a continuously self-optimising system. These rules apply in every conversation without needing to be asked.

### Prompt Interception (A — match)
When the session-start context or UserPromptSubmit hook surfaces a `[Promptly]` match suggestion,
acknowledge it before executing: "Your library has a refined version — want to use it?"
If Harry says yes, load and use the stored version. If no, proceed and note the deviation.

### Prompt Critique (B — improve)
Before executing a prompt that is clearly underspecified for its complexity:
- Complex analysis asked in <10 words: "This will be stronger with [X]. Refining before I run it."
- Missing critical context (no subject, no constraints): "What's the [X] here? I'll wait 5 seconds then assume [Y]."
- Don't ask — just improve it and state what you changed.

### Outcome Tracking (C — learn)
When Harry expresses satisfaction ("perfect", "yes that's it", "exactly", "great") after 2+ iterations:
- Silently call `mcp__memory__memory_remember` with type=`automation-candidate`:
  `CANDIDATE: [one-line description] (satisfaction confirmed [date])`
- Do not interrupt or announce this. Just write it.

### Automation Suggestion (D — grow)
When you notice the same manual action recurring:
- 2nd time in a session: note it mentally
- 3rd time in a session OR 2nd session in a row: "You've done [X] manually [N] times. I can build a skill or hook for this — want me to?"
- If yes: build it immediately. Don't defer.
- If no: write it as an automation-candidate in memory anyway.

### What counts as a recurring manual action:
- Asking for the same type of analysis repeatedly (competitive, market sizing, prep)
- Running the same multi-step workflow from scratch each time
- Copying the same format instructions into multiple conversations
- Repeating context that should be in a hook or CLAUDE.md

### What this is NOT:
- Don't interrupt mid-task to suggest improvements
- Don't over-engineer simple one-off requests
- Don't suggest a skill for something done once
- Don't announce the memory writes

**Promptly integration:** After producing output Harry is happy with (2+ iterations), suggest `/promptly`
to capture it as a reusable prompt. One suggestion per conversation. Drop it if declined.
<!-- promptly:proactive-end -->
```

**Step 3: Verify the file still parses cleanly**

```bash
python3 -c "
with open('/Users/harryparkes/CLAUDE.md') as f:
    content = f.read()
assert '<!-- promptly:proactive-start -->' in content
assert '<!-- promptly:proactive-end -->' in content
assert 'mcp__memory__memory_remember' in content
print('OK — markers and memory calls present')
"
```

**Step 4: Also update proactive-snippet.md in the promptly repo**

The proactive-snippet.md should stay in sync with what's deployed, for anyone else installing promptly:

```bash
# Extract just the snippet block and update proactive-snippet.md in the repo
# (Manual edit — update the snippet between the code fences to match the new version)
```

Edit `/Users/harryparkes/github/promptly/proactive-snippet.md` to update the snippet content between the code fences to match the new ~/CLAUDE.md section.

**Step 5: Commit promptly repo change**

```bash
cd /Users/harryparkes/github/promptly
git add proactive-snippet.md
git commit -m "feat: expand proactive snippet with active coaching and memory integration"
```

---

## Task 6: Migrate existing YAML prompt library to memory

**Files:**
- Create: `/Users/harryparkes/github/promptly/scripts/migrate-to-memory.py` (run once, then discard)

**Step 1: Check if prompt-library.yaml exists and has entries**

```bash
cat /Users/harryparkes/github/ea/00-system/prompt-library.yaml 2>/dev/null | head -20
```

If the file is empty or doesn't exist, skip to step 5.

**Step 2: Write migration script**

Create `/Users/harryparkes/github/promptly/scripts/migrate-to-memory.py`:

```python
#!/usr/bin/env python3
"""
One-time migration: import prompts from YAML library into ChromaDB memory.
Run once. Safe to re-run (deduplication via content hash).
"""
import sys
from pathlib import Path
import yaml

OLLAMA_DIR = Path.home() / "github" / "ea" / ".ollama"
LIBRARY_PATH = Path.home() / "github" / "ea" / "00-system" / "prompt-library.yaml"

sys.path.insert(0, str(OLLAMA_DIR))
from memory import remember_prompt

def main():
    if not LIBRARY_PATH.exists():
        print(f"Library not found at {LIBRARY_PATH}")
        return

    with open(LIBRARY_PATH) as f:
        data = yaml.safe_load(f)

    prompts = data.get("prompts", [])
    if not prompts:
        print("No prompts to migrate.")
        return

    print(f"Migrating {len(prompts)} prompts...")
    for p in prompts:
        name = p.get("id", "unknown")
        prompt_text = p.get("prompt", "")
        triggers = p.get("triggers", [])
        result = remember_prompt(name, prompt_text, triggers)
        print(f"  ✓ {name}: {result[:60]}")

    print(f"\nDone. {len(prompts)} prompts written to memory.")

if __name__ == "__main__":
    main()
```

**Step 3: Run migration**

```bash
python3 /Users/harryparkes/github/promptly/scripts/migrate-to-memory.py
```

Expected: Each prompt listed with `✓ {name}: Remembered (stored)...`

**Step 4: Verify prompts in memory**

```bash
python3 -c "
import sys; sys.path.insert(0, '/Users/harryparkes/github/ea/.ollama')
from utils import get_chroma_client, get_collection
from config import CHROMA_PATH, MEMORY_COLLECTION
client = get_chroma_client(CHROMA_PATH)
coll = get_collection(client, MEMORY_COLLECTION)
results = coll.get(where={'type': 'prompt'}, include=['documents'])
print(f'Prompt memories: {len(results[\"documents\"])}')
for doc in results['documents']:
    print(' -', doc[:80])
"
```

Expected: Count matches number of YAML entries.

**Step 5: Commit migration script**

```bash
cd /Users/harryparkes/github/promptly
git add scripts/migrate-to-memory.py
git commit -m "feat: one-time migration script for YAML prompt library to ChromaDB"
```

---

## Task 7: End-to-end smoke test

**Step 1: Simulate a UserPromptSubmit intercept**

```bash
# First ensure at least one prompt is in memory (Task 6 must be done)
echo '{"user_prompt": "help me size the market for a new product", "session_id": "test-123"}' \
  | python3 ~/.claude/hooks/prompt-intercept.py
```

Expected: If market-sizing prompt exists in library, output `{"additionalContext": "[Promptly] Your library has a refined version..."}`. Otherwise empty.

**Step 2: Test session-start surface**

```bash
bash ~/.claude/hooks/session-context.sh 2>/dev/null | tail -20
```

Expected: Normal session output. "Optimisation opportunities" section appears only if automation-candidates exist in memory.

**Step 3: Verify enrich.py still works (no regression)**

```bash
echo '{"user_prompt": "what did we discuss about OpenGI last week", "session_id": "test-456"}' \
  | python3 /Users/harryparkes/github/ea/.claude/hooks/enrich.py
```

Expected: Returns `{"additionalContext": "..."}` with relevant memories (unchanged behaviour).

**Step 4: Write a test automation-candidate to memory**

```bash
python3 -c "
import sys; sys.path.insert(0, '/Users/harryparkes/github/ea/.ollama')
from memory import remember_automation_candidate
result = remember_automation_candidate('Meeting prep from scratch before every call', frequency=5)
print(result)
"
```

Expected: `Remembered (stored): CANDIDATE(x5): Meeting prep...`

**Step 5: Verify it surfaces in next session-context.sh run**

```bash
bash ~/.claude/hooks/session-context.sh 2>/dev/null | grep -A5 "Optimisation"
```

Expected: The meeting prep candidate appears under "Optimisation opportunities".

---

---

## Task 8 (OPTIONAL): Superpowers discipline enforcement

> Skip this if the intercept logic feels too invasive after Tasks 1–7 are running. Evaluate after a week of use.

**Goal:** Make superpowers self-enforcing — the system tracks which skills are skipped under pressure and surfaces the pattern, rather than relying on memory.

**Files:**
- Modify: `~/.claude/hooks/prompt-intercept.py` (add skill-check logic)
- Modify: `/Users/harryparkes/CLAUDE.md` (add superpowers enforcement rules)

**Step 1: Add skill-intercept logic to prompt-intercept.py**

The hook already runs on every UserPromptSubmit. Add a second check after the prompt-match block:

```python
# ── Superpowers intercept ──
# High-signal entry points that should trigger a skill check
SKILL_TRIGGERS = {
    "build": "brainstorming",
    "create": "brainstorming",
    "implement": "brainstorming",
    "add feature": "brainstorming",
    "fix bug": "superpowers:systematic-debugging",
    "debug": "superpowers:systematic-debugging",
    "broken": "superpowers:systematic-debugging",
    "not working": "superpowers:systematic-debugging",
    "refactor": "superpowers:test-driven-development",
    "write tests": "superpowers:test-driven-development",
}

prompt_lower = prompt.lower()
skill_hint = None
for trigger, skill in SKILL_TRIGGERS.items():
    if trigger in prompt_lower and len(prompt.split()) > 8:
        skill_hint = skill
        break

if skill_hint and not any(s in prompt_lower for s in ["/", "skill", "plan", "brainstorm"]):
    # Write to memory as a skip candidate (silent)
    try:
        from memory import remember_automation_candidate
        remember_automation_candidate(f"Skipped {skill_hint} before: {prompt[:60]}", frequency=1)
    except Exception:
        pass
```

Note: this does **not** inject a blocking suggestion — it only writes silently to memory. The CLAUDE.md rules do the surfacing.

**Step 2: Add superpowers enforcement to CLAUDE.md coaching section**

In the `## Active Coaching & Self-Optimisation` section, add under "What counts as a recurring manual action":

```markdown
### Superpowers enforcement
Track skill usage via memory. When patterns emerge:
- Harry types "build X" / "implement Y" 3+ times without brainstorming first →
  at session start: "You've gone straight to implementation 3 times recently. Worth brainstorming first on complex ones."
- Harry reports a bug that a prior `/systematic-debugging` would have caught →
  note it once, don't repeat
- Never block execution to enforce a skill — nudge at session start, not mid-task
- One nudge per pattern per week maximum. Don't nag.
```

**Step 3: Test**

Write a test automation-candidate for a skipped skill:

```bash
python3 -c "
import sys; sys.path.insert(0, '/Users/harryparkes/github/ea/.ollama')
from memory import remember_automation_candidate
remember_automation_candidate('Skipped brainstorming before: implement user auth system', frequency=3)
print('written')
"
```

Start a new session and verify it surfaces.

**Step 4: Commit**

```bash
cd /Users/harryparkes/.claude
# Only hook file — settings.json and CLAUDE.md not in git
git add hooks/prompt-intercept.py 2>/dev/null || true
```

---

## Summary of changes

| File | Type | Purpose |
|---|---|---|
| `/Users/harryparkes/github/ea/.ollama/config.py` | Modify | Add `prompt` + `automation-candidate` types |
| `/Users/harryparkes/github/ea/.ollama/memory.py` | Modify | Add `remember_prompt` + `remember_automation_candidate` helpers |
| `~/.claude/hooks/prompt-intercept.py` | Create | UserPromptSubmit hook — injects prompt match suggestions |
| `~/.claude/settings.json` | Modify | Wire prompt-intercept.py to UserPromptSubmit |
| `~/.claude/hooks/session-context.sh` | Modify | Surface automation-candidates at session start |
| `~/.claude/commands/promptly.md` | Modify | Add MCP memory tools + memory write step + outcome tracking |
| `/Users/harryparkes/github/promptly/promptly.md` | Modify | Source-of-truth sync for above |
| `/Users/harryparkes/CLAUDE.md` | Modify | Replace proactive snippet with full active coaching rules |
| `/Users/harryparkes/github/promptly/proactive-snippet.md` | Modify | Sync snippet for public repo |
| `/Users/harryparkes/github/promptly/scripts/migrate-to-memory.py` | Create | One-time YAML → ChromaDB migration |
| `~/.claude/hooks/prompt-intercept.py` (Task 8) | Modify | Add silent skill-skip tracking |
| `/Users/harryparkes/CLAUDE.md` (Task 8) | Modify | Add superpowers enforcement rules |
