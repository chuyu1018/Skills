# skills

Personal Claude Code skills collection.

## Skills

| Name | Description |
|------|-------------|
| [rcy-trip](rcy-trip/) | AI 协作旅行攻略 SOP — 给定目的地，按"AI 收敛 / 人发散"的分工模式生成个性化深度行程 |

## Installation

Clone this repo and symlink each skill into `~/.claude/skills/`:

```bash
git clone https://github.com/chuyu1018/skills.git ~/Documents/skills

# Symlink individual skills
ln -s ~/Documents/skills/rcy-trip ~/.claude/skills/rcy-trip
```

After symlinking, restart Claude Code (or start a new session) and the skill will be discoverable.

## Skill format

Each skill lives in its own directory containing a `SKILL.md` with YAML frontmatter. See [Claude skills documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills) and [agentskills.io specification](https://agentskills.io/specification) for details.
