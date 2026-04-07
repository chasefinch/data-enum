# Agent Notes Index

This directory contains notes and learnings that AI agents use to improve accuracy and speed when working with this codebase.

## Purpose

These notes serve as a persistent memory system for AI agents (like Claude Code) to:
- Record patterns and conventions discovered in the codebase
- Document common pitfalls and their solutions
- Track architectural decisions and their rationale
- Build institutional knowledge across development sessions

**CRITICAL**: Each new conversation session starts fresh. These notes are your ONLY memory across sessions. Always read relevant notes at the start of work, and always update them with new learnings so future sessions benefit from your discoveries.

**IMPORTANT FOR CLAUDE CODE**: Do NOT use the built-in auto memory system (`~/.claude/projects/.../memory/MEMORY.md`). Use ONLY this project-level system in `docs/agents/`. This ensures all learnings are versioned, shared with the team, and organized properly.

## Usage Guidelines for Agents

When working with this codebase:

1. **Always read relevant notes first** - Before starting a task, check if there are existing notes that could inform your approach
2. **Update notes after significant learnings** - When you discover something important, update the appropriate note file
3. **Be specific and actionable** - Notes should contain concrete examples and clear guidance
4. **Keep notes organized** - Add new insights to the appropriate section, create new sections as needed
5. **Reference locations** - Include file paths and line numbers when referencing specific code
6. **Use subagents proactively** - Don't hesitate to use the Task tool with specialized subagents (Explore, Bash, general-purpose, Plan) when they're appropriate for the work. Launch them in parallel when tasks are independent.

## Note Template

When adding new notes, use this structure:

```markdown
## [Topic/Pattern Name]

**Context**: Brief description of when this applies

**Problem**: What issue does this address?

**Solution**: The recommended approach

**Example**: Code example or reference to existing code

**Related**: Links to other relevant notes or documentation
```
