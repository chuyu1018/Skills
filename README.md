# chuyu-skills

Personal Claude Code skills marketplace by [@chuyu1018](https://github.com/chuyu1018).

## Skills available

| Plugin | Description |
|--------|-------------|
| [`rcy-trip`](rcy-trip/) | AI 协作旅行攻略 SOP — 三步生成个性化深度行程 |
| [`social-media-agent`](social-media-agent/) | Social media content analysis and generation |

## Installation

### Recommended: as a Claude Code plugin

In Claude Code, run:

```
/plugin marketplace add chuyu1018/skills
/plugin install rcy-trip@chuyu-skills
```

Replace `rcy-trip` with any plugin name from the table above. After install, restart Claude Code (or start a new session) and the skill will auto-trigger or be invocable as `/<plugin-name>`.

To list / update / remove later:

```
/plugin marketplace list
/plugin update rcy-trip@chuyu-skills
/plugin uninstall rcy-trip@chuyu-skills
```

### Alternative 1: one-line curl (single skill, no updates)

For people without `/plugin` support, drop just the SKILL.md into place:

```bash
mkdir -p ~/.claude/skills/rcy-trip && \
curl -fsSL https://raw.githubusercontent.com/chuyu1018/skills/main/rcy-trip/skills/rcy-trip/SKILL.md \
  -o ~/.claude/skills/rcy-trip/SKILL.md
```

### Alternative 2: clone + symlink (manual updates via git pull)

```bash
git clone https://github.com/chuyu1018/skills.git ~/Documents/chuyu1018-skills
ln -s ~/Documents/chuyu1018-skills/rcy-trip/skills/rcy-trip ~/.claude/skills/rcy-trip
```

Update with:

```bash
cd ~/Documents/chuyu1018-skills && git pull
```

## Repo layout

```
.
├── .claude-plugin/
│   └── marketplace.json           # marketplace manifest
├── rcy-trip/                      # plugin
│   ├── .claude-plugin/plugin.json
│   └── skills/rcy-trip/SKILL.md
└── social-media-agent/            # plugin
    ├── .claude-plugin/plugin.json
    └── skills/social-media-agent/
        ├── SKILL.md
        ├── references/
        └── scripts/
```

Each plugin follows the [Claude Code Plugin spec](https://docs.claude.com/en/docs/agents-and-tools/plugins): SKILL.md must live at `<plugin>/skills/<skill-name>/SKILL.md`.

## License

MIT — feel free to fork, copy patterns, or send PRs.
