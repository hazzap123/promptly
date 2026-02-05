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

Promptly notices when you're in an exploratory pattern:
- 3+ clarification rounds on the same topic
- Format iterations ("try it as a table", "add X section")
- Pivots ("actually, what I really want is...")
- Satisfaction signals ("yes, that's exactly it")

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

Create a prompt library file in your project:

```yaml
# 00-system/prompt-library.yaml

prompts: []
```

If you use a different location, update the path in `promptly.md` (line 28).

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

You explored competitive analysis, iterating through:
- Initial ask: "who are the competitors"
- Refined to: feature comparison matrix
- Added: positioning analysis
- Final output: strategic recommendations

Here's your distilled prompt:

---
Analyze the competitive landscape for [PRODUCT] in [MARKET].

Structure:
1. Direct competitors (same solution, same customer)
2. Indirect competitors (different solution, same problem)
3. Feature comparison matrix
4. Positioning map (2x2)
5. Strategic implications

For each competitor: funding, traction, strengths, weaknesses.
---

Triggers: "competitive analysis", "who are the competitors"

Add to library as 'competitive-analysis'? [Y/n]
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
  - id: competitive-analysis
    name: "Competitive Analysis"
    description: "Landscape analysis with positioning and strategic implications"
    prompt: |
      Analyze the competitive landscape for [PRODUCT] in [MARKET].

      Structure:
      1. Direct competitors (same solution, same customer)
      2. Indirect competitors (different solution, same problem)
      3. Feature comparison matrix
      4. Positioning map (2x2)
      5. Strategic implications
    triggers:
      - "competitive analysis"
      - "who are the competitors"
      - "competitor landscape"
    created: 2026-02-05
```

## Customization

### Library Location

Default: `00-system/prompt-library.yaml`

Change by editing line 28 in `promptly.md`:
```
**Prompt library location:** @your/preferred/path.yaml
```

### User Context

Promptly reads from `CLAUDE.md` and `00-system/user-profile.yaml` to personalize prompts. Document your:
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

## License

MIT

---

*Turn exploration into assets. Build your prompt library over time.*
