# Promptly: Proactive Snippet

Add the following snippet to enable proactive prompt capture — so Claude detects
exploratory patterns during normal conversation and suggests running `/promptly`.

## Installation

### Global (recommended — works in every project)

```bash
# Extract just the snippet and append it to your global CLAUDE.md
sed -n '/<!-- promptly:proactive-start -->/,/<!-- promptly:proactive-end -->/p' \
  proactive-snippet.md >> ~/.claude/CLAUDE.md
```

### Per-project

```bash
# Append to a specific project's CLAUDE.md
sed -n '/<!-- promptly:proactive-start -->/,/<!-- promptly:proactive-end -->/p' \
  proactive-snippet.md >> /path/to/project/CLAUDE.md
```

### Manual

Copy everything between the `<!-- promptly -->` markers below into your `CLAUDE.md`:

```markdown
<!-- promptly:proactive-start -->
## Prompt Capture (Promptly)

When you notice the user iterating on a conversation — refining output format, adding/removing
sections, pivoting intent, or expressing satisfaction after multiple rounds — consider suggesting
`/promptly` to capture the pattern as a reusable prompt.

**When to suggest:**
- 2+ rounds refining the same output (format changes, section additions, restructuring)
- User pivots to reveal real intent ("actually, what I really want is...")
- Satisfaction after iteration ("yes, that's it", "perfect", "exactly what I need")
- User indicates reuse intent ("I'll use this template going forward")

**When NOT to suggest:**
- Simple Q&A, debugging, or troubleshooting
- First iteration on something (wait for the refinement loop)
- User is executing a predefined plan or checklist
- Already suggested once in this conversation and user declined

**How to suggest:** After delivering the output the user is happy with, briefly note the
iteration pattern and ask if they'd like to run `/promptly` to save it. Keep it to 1-2 sentences.
Don't interrupt mid-iteration — wait for the satisfaction signal.
<!-- promptly:proactive-end -->
```

---

## Why this is needed

The `/promptly` skill only loads when explicitly invoked. Without this snippet, Claude has no
awareness of prompt capture during normal conversation, so proactive mode never triggers.

This snippet is intentionally lightweight — it tells Claude *when* to suggest `/promptly`, and the
skill itself handles the heavy lifting of analysis, distillation, and library management.
