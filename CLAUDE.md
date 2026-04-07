# Claude Code — Data Enum

An alternative to the built-in Python `enum` implementation. Pure Python package.

## Before You Start

`docs/agents/` contains notes from past sessions that may be relevant to your task. Consult when you need context; update when you learn something non-obvious.

## When You...

- **Learn something non-obvious** → Add a "When You..." entry here (keep this file under 100 lines), or update `docs/agents/`.
- **Run tests or CI commands** → See Quick Reference below

## Quick Reference

| Task | Command |
|---|---|
| **Full pipeline** | `make` (sync, configure, format, lint, check, test) |
| **Format** | `make format` |
| **Lint** | `make lint` (format first!) |
| **Type check** | `make check` |
| **Test** | `make test` |

Always activate the venv first: `source .venv/bin/activate`

## Skills & Tools

Custom Claude Code skills live in `.claude/skills/`. MCP servers may also be installed at the IDE level — discover available tools before assuming they don't exist.

## Key Directories

- `data_enum/` — Main package source code
- `tests/` — Test files
- `requirements/` — Requirements files

## Agent Notes

`docs/agents/` is the shared knowledge base for all LLM agents. Version-controlled and team-visible. Keep notes accurate, concise, and actionable.
