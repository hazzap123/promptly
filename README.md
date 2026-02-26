# Promptly

A [Claude Code](https://claude.ai/code) skill that turns messy exploratory conversations into reusable single-shot prompts.

## The Problem

When you explore a problem with Claude — iterating, clarifying, refining — you often end up with a great output. But next time you need the same thing, you start from scratch.

**Promptly captures those patterns.**

## How It Works

After a successful exploration, run `/promptly` and it will:

1. Analyze the conversation journey
2. Distill a refined, reusable prompt
3. Save it to your prompt library with trigger keywords

Next time you start a similar task, it offers your refined version.

## Features

| Mode | What It Does |
|------|--------------|
| **Distill** (default) | Extract reusable prompts from exploratory conversations |
| **Match** | Surface relevant prompts from your library when starting new tasks |
| **Proactive** | Offers to capture patterns when it notices you iterating |

### Proactive Detection

> **Requires setup:** Add the proactive snippet to your `CLAUDE.md` — see [Setup](#2-enable-proactive-mode-recommended).

Promptly notices when you're in an exploratory pattern:
- 2+ rounds refining the same output (format changes, restructuring, adding sections)
- Pivots that reveal real intent ("actually, what I really want is...")
- Satisfaction after iteration ("yes, that's it", "perfect", "exactly what I need")
- Reuse signals ("I'll use this template going forward")

When detected, it offers to capture — no need to remember to run `/promptly`.

### User Context Aware

If you have a `CLAUDE.md` or user profile, Promptly adapts distilled prompts to match your:
- Communication style
- Preferred frameworks
- Domain vocabulary

## Installation

```bash
curl -o ~/.claude/commands/promptly.md \
  https://raw.githubusercontent.com/hazzap123/promptly/main/promptly.md
```

Or clone and copy:

```bash
git clone https://github.com/hazzap123/promptly.git
cp promptly/promptly.md ~/.claude/commands/
```

## Setup

### 1. Create a prompt library

Start from scratch:

```yaml
# prompt-library.yaml

prompts: []
```

Or copy the example library to get started immediately:

```bash
curl -o prompt-library.yaml \
  https://raw.githubusercontent.com/hazzap123/promptly/main/examples/prompt-library.yaml
```

This includes four ready-to-use prompts: Picard mode (truth over validation), belief reframing, content review, and strategic landscape mapping.

Place it in your project root, or wherever you prefer. If you use a different location, note it in your `CLAUDE.md` — Promptly will discover it automatically.

### 2. Enable proactive mode (recommended)

The `/promptly` skill only loads when you invoke it. For Claude to *proactively* detect prompt-worthy patterns during normal conversation, add a lightweight snippet to your `CLAUDE.md`.

**Global (works in every project — recommended):**

```bash
# Append the snippet to your global CLAUDE.md
sed -n '/<!-- promptly:proactive-start -->/,/<!-- promptly:proactive-end -->/p' \
  proactive-snippet.md >> ~/.claude/CLAUDE.md
```

**Per-project:**

```bash
# Append to a specific project's CLAUDE.md
sed -n '/<!-- promptly:proactive-start -->/,/<!-- promptly:proactive-end -->/p' \
  proactive-snippet.md >> /path/to/project/CLAUDE.md
```

Or manually copy the snippet from [`proactive-snippet.md`](proactive-snippet.md). See that file for the full snippet content.

This tells Claude *when* to suggest `/promptly` — the skill itself handles the rest.

Without this step, proactive mode won't trigger and you'll need to remember to run `/promptly` manually after exploratory conversations.

## Usage

### After exploring a problem:

```
/promptly
```

Analyzes your conversation and offers to save a distilled prompt.

### Check for existing prompts:

```
/promptly match
```

Searches your library for prompts matching your current context.

### Example: Distill

```
/promptly

Analyzing your conversation...

You explored code review, iterating through:
- Initial ask: "review this PR"
- Added: security focus
- Refined: severity levels for issues
- Added: summary with recommended action

Here's your distilled prompt:

---
Review [CODE/PR] with focus on:

1. **Critical** — Security vulnerabilities, data loss risks, breaking changes
2. **Important** — Bugs, performance issues, error handling gaps
3. **Suggestions** — Style, naming, simplification opportunities

For each issue:
- File and line reference
- What's wrong and why it matters
- Concrete fix suggestion

End with: **Recommendation** — Approve / Request changes / Needs discussion
---

Triggers: "review this", "code review", "check this PR"

Add to library as 'code-review'? [Y/n]
```

### Example: Proactive Offer

```
User: "Actually, can you add a section for open commitments?"

Claude: [Provides updated format]

User: "Yes, that's exactly what I need."

---
This looks like a prompt pattern worth capturing.

What I noticed:
- Initial ask: "prep me for meeting with X"
- Added: relationship history
- Added: open commitments
- Final form: structured prep doc

Want me to distill this as a reusable prompt?

[Yes, capture it] [No, just continue]
---
```

## Library Format

Prompts are stored in YAML:

```yaml
prompts:
  - id: code-review
    name: "Code Review"
    description: "Structured PR review with severity levels and actionable feedback"
    prompt: |
      Review [CODE/PR] with focus on:

      1. **Critical** — Security vulnerabilities, data loss risks, breaking changes
      2. **Important** — Bugs, performance issues, error handling gaps
      3. **Suggestions** — Style, naming, simplification opportunities

      For each issue:
      - File and line reference
      - What's wrong and why it matters
      - Concrete fix suggestion

      End with: **Recommendation** — Approve / Request changes / Needs discussion
    triggers:
      - "review this"
      - "code review"
      - "check this PR"
    created: YYYY-MM-DD
```

## Customization

### Library Location

Default: `prompt-library.yaml` in the project root.

Override by adding a line to your `CLAUDE.md`:
```
Prompt library: ./path/to/prompt-library.yaml
```

### User Context

Promptly reads from `CLAUDE.md` and `user-profile.yaml` (if present) to personalise prompts. Document your:
- Communication preferences
- Frameworks you use
- Domain vocabulary

Distilled prompts will incorporate these automatically.

### Proactive Sensitivity

Edit the `<proactive_detection>` section to adjust when Promptly offers to capture. Add or remove trigger signals based on your workflow.

## Security

- **Local only** — Reads and writes files only within your project directory
- **No network access** — Cannot transmit data externally
- **No code execution** — Cannot run shell commands (Bash not in allowed-tools)
- **Plain text storage** — Prompt library is stored as YAML. Avoid capturing conversations containing credentials, API keys, or secrets
- **User context stays local** — Reads CLAUDE.md for personalization but doesn't store or expose its contents

### Allowed Tools

```yaml
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
```

No Bash, no web access, no subagent spawning.

## Requirements

- [Claude Code](https://claude.ai/code) CLI

## Contributing

Issues, prompt examples, and improvements welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT

---

*Turn exploration into assets. Build your prompt library over time.*
