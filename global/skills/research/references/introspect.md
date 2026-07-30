# Introspect

Analyze session transcripts for usage patterns. Output actionable improvement recommendations.

## Role

Act as a staff engineer conducting a retrospective on actual use.
Review actual use, not intended use. Use evidence over intuition.

## Objective

Analyze all Claude Code session history and produce:
1. Frequency breakdown of actual usage patterns
2. Candidates for skill extraction (repeated multi-step workflows)
3. Candidates for autonomous agents (persistent loops, not one-shots)
4. CLAUDE.md/AGENTS.md updates (principles, not pragmatics)
5. Workflows to retire or consolidate

## Data Sources

Session transcripts live at `~/.claude/projects/`. Structure:
- Each project directory contains `.jsonl` files (one per session)
- `subagents/` subdirectories contain subagent transcripts (skip for top-level analysis)
- Record types: `user` (human messages), `assistant` (model responses), `progress` (hooks/system)

### JSONL Record Format

```
{
  "type": "user" | "assistant" | "progress",
  "message": {
    "role": "user" | "assistant",
    "content": "..." | [{ "type": "text", "text": "..." }, { "type": "tool_use", ... }]
  },
  "timestamp": "ISO-8601",
  "cwd": "/path/to/project",
  "sessionId": "uuid",
  "gitBranch": "branch-name"
}
```

Slash commands appear as: `<command-name>/skill-name</command-name>` in user message content.
Tool calls appear as `{ "type": "tool_use", "name": "ToolName", "input": {...} }` in assistant content.

## Durable Mining Contract

Effectiveness mining is an opt-in research lane that uses explicit transcript and
skill-log inputs.
Redact before reporting.
Fail closed when secret-like content remains unresolved.
Join evidence stores only when refs match.
Report missing coverage instead of inferring effectiveness from sparse data.
Default reports contain counts and refs, not raw turn text.

## Durable Command Expansion Checklist

When the analysis needs broader coverage, extend the research query and its
falsification checks to extract:

### Quantitative
- **Sessions per project** (top 20)
- **Tool usage** by call count (top 25)
- **Slash commands** invoked by user (parse `<command-name>` tags)
- **Skill tool calls** invoked by Claude (from `Skill` tool_use blocks)
- **Subagent types** spawned (from `Agent` tool_use blocks)
- **Bash command frequency** (first word + git/gh subcommands)
- **File types edited** (by extension from Edit/Write tool calls)
- **Most edited files** (by filename)
- **User intent classification** (keyword-match into categories)
- **Repeated user messages** (normalized, count >= 3)

### Qualitative
- Sample 80 random user messages for manual pattern recognition.
- Extract user corrections and frustrations from messages containing "wrong", "not what I", "still", or "again".

### Filters
- Skip `subagents/` directories during top-level analysis.
- Skip tool_result content because it contains response data, not intent.
- Skip skill expansion text, including messages containing "Base directory for this skill:".
- Cap sampled messages at 300 chars and skip messages shorter than 3 chars.

## Output Format

Present findings in this structure:

### 1. What You Do Most (ranked by frequency)
Table: Activity | % of usage | Evidence

### 2. Skill Candidates
Table: Proposed Skill | Repeated Pattern | Current State (ad-hoc / manual / partial)

### 3. Agent Candidates
Table: Proposed Agent | Why Autonomous | Evidence (not one-shot skills — persistent loops)

### 4. Instruction Updates
Table: Principle | Evidence (corrections, friction, repeated mistakes)
Keep to underlying principles, not specific pragmatic rules.

### 5. Retirements
Skills, workflows, or patterns that data shows are unused or superseded.

## Constraints

- Use evidence first. Cite session data for every recommendation.
- Keep analysis agent-agnostic. Apply it to any coding agent, not only Claude Code.
- Prefer principles over pragmatics. Keep CLAUDE.md updates philosophical, not procedural.
- Remove fluff categories.
- Cut any recommendation with fewer than 3 supporting data points.
- Respect the user's time. Keep findings scannable in under 2 minutes.
