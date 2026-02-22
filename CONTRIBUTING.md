# Contributing to Promptly

Thanks for your interest in improving Promptly!

## Ways to Contribute

### Report Issues
- Bug reports: Something not working as expected
- Feature requests: Ideas for new capabilities
- Documentation: Unclear instructions or missing info

### Submit Changes

1. Fork the repository
2. Create a branch (`git checkout -b improve-detection`)
3. Make your changes to `promptly.md`
4. Test with Claude Code (`cp promptly.md ~/.claude/commands/`)
5. Commit with a clear message
6. Open a Pull Request

### Good First Contributions

- Add new trigger phrases for existing modes
- Improve examples in the skill or README
- Add edge case handling
- Fix typos or clarify documentation

## Project Structure

| File | Purpose |
|------|---------|
| `promptly.md` | The skill — loaded when `/promptly` is invoked |
| `proactive-snippet.md` | CLAUDE.md snippet — enables always-on pattern detection |
| `README.md` | User-facing documentation |
| `CONTRIBUTING.md` | This file |

### Skill sections

The skill (`promptly.md`) is a single markdown file with:

| Section | Purpose |
|---------|---------|
| `---` frontmatter | Name, description, allowed tools |
| `<objective>` | What the skill does |
| `<context>` | File paths and variables |
| `<proactive_detection>` | Rules for when to offer prompt capture |
| `<process>` | Step-by-step instructions for Claude |
| `<examples>` | Show expected behavior |
| `<edge_cases>` | Handle unusual situations |

## Guidelines

- **Keep it simple** — One file, minimal complexity
- **Test your changes** — Run `/promptly` and verify behavior
- **No new dependencies** — The skill should remain self-contained
- **Security conscious** — Don't add tools that aren't needed (especially Bash)

## Questions?

Open an issue — happy to discuss ideas before you start coding.
