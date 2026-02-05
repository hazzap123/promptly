# Promptly

A Claude Code skill that turns messy exploratory conversations into reusable single-shot prompts.

## What It Does

When you explore a problem with Claude — iterating, clarifying, refining — you often end up with a great output format. But next time you need the same thing, you start from scratch.

**Promptly captures those patterns.**

After a successful exploration, run `/promptly` and it will:
1. Analyze the conversation journey
2. Distill a refined, reusable prompt
3. Save it to your prompt library with trigger keywords

Next time you start a similar task, it offers your refined version.

## Features

- **Distill mode** — Extract reusable prompts from exploratory conversations
- **Match mode** — Surface relevant prompts from your library when starting new tasks
- **Proactive detection** — Offers to capture patterns when it notices you iterating (3+ refinements, format changes, "actually what I want is..." pivots)
- **User context aware** — Adapts prompts to your communication style and frameworks (reads from CLAUDE.md)

## Installation

```bash
# Download to your Claude Code commands folder
curl -o ~/.claude/commands/promptly.md https://raw.githubusercontent.com/hazzap123/promptly/main/promptly.md
```

Or clone and copy:
```bash
git clone https://github.com/hazzap123/promptly.git
cp promptly/promptly.md ~/.claude/commands/
```

## Setup

Create a prompt library file in your project:

```yaml
# 00-system/prompt-library.yaml (or wherever you prefer)

prompts: []
```

Update the library path in `promptly.md` if you use a different location.

## Usage

### After an exploratory conversation:
```
/promptly
```

Analyzes your conversation and offers to save a distilled prompt.

### Check for existing prompts:
```
/promptly match
```

Searches your library for prompts matching your current context.

### Proactive mode:
When you've been iterating on a format (3+ refinements), promptly will offer:

```
This looks like a prompt pattern worth capturing.

What I noticed:
- Initial ask: "prep me for meeting with X"
- Added: relationship history
- Added: open commitments
- Final form: structured prep doc

Want me to distill this as a reusable prompt?
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

### User Context

Promptly reads from `CLAUDE.md` and `00-system/user-profile.yaml` to adapt prompts to your style. If you have frameworks or preferences documented there, distilled prompts will incorporate them.

### Proactive Detection

Edit the `<proactive_detection>` section in `promptly.md` to adjust when it offers to capture patterns.

## License

MIT

---

Built for [Claude Code](https://claude.ai/code)
