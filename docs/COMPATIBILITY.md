# Platform Compatibility

## Supported Agents

All skills use the universal [SKILL.md standard](https://agentskills.io) with YAML
frontmatter + Markdown instructions. They are compatible with any agent that supports
the SKILL.md format.

## Installation Paths

| Agent | Skill Path (Project) | Skill Path (Global) | Notes |
|:---|:---|:---|:---|
| **Claude Code** | `.claude/skills/` | `~/.claude/skills/` | Native support |
| **Gemini CLI** | `.gemini/skills/` | `~/.gemini/skills/` | Native support |
| **Antigravity** | `.gemini/skills/` | `~/.gemini/skills/` | Same as Gemini CLI |
| **Cursor** | `.cursor/skills/` | `~/.cursor/skills/` | Check version |
| **GitHub Copilot** | `.github/skills/` | N/A | Via extensions |
| **Codex (OpenAI)** | `.codex/skills/` | N/A | Via extensions |
| **Windsurf** | `.windsurf/skills/` | N/A | Via extensions |

## Unified Installation

To support multiple agents from a single source:

```bash
# 1. Copy skills to your project
cp -r skills/ ./agent-skills/

# 2. Create symlinks for each agent you use
ln -s ./agent-skills .claude/skills
ln -s ./agent-skills .gemini/skills
ln -s ./agent-skills .cursor/skills
```

## Skill Loading Behavior

Skills are loaded using a 3-tier progressive disclosure pattern:

1. **L1 (Discovery)**: Agent reads ONLY the YAML frontmatter (name + description) from each SKILL.md
2. **L2 (Activation)**: When a skill is triggered, agent reads the full SKILL.md body
3. **L3 (Deep Reference)**: When the skill references a file in `references/`, agent reads that file on demand

This ensures minimal context window usage until a skill is actually needed.

## Requirements

These skills are instruction-only (no runtime dependencies). The optional Python
scripts in `scripts/` require:
- Python 3.8+
- numpy
- scipy
- statsmodels (for power analysis)
- scikit-learn (for imputation methods)
- econml (for HTE estimation, optional)

Install optional dependencies:
```bash
pip install numpy scipy statsmodels scikit-learn econml
```
