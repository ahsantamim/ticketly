---
name: analyze
description: Read-only, interactive architecture walkthrough of how a Ticketly Linear issue (TIC-*) would be implemented in the existing codebase, one section at a time with understanding checkpoints. Never writes code. Use only when the user explicitly invokes /analyze.
argument-hint: "[TIC-123]"
disable-model-invocation: true
---

# Analyze a Linear task before building it (read-only)

This is a guided walkthrough that helps the user, a software engineer, understand how a Linear issue would be implemented in **this** product before any code is written. It is not a code-generation workflow. When the user is ready to build, they'll invoke `/implementation-linear-task`.

Issue: `$ARGUMENTS` (if empty, see Phase 1).

## Strict read-only rules

These rules hold for the entire skill, including after the walkthrough ends:

- **Never** create, edit, move, or delete application files, config, migrations, or tests. Don't use Write, Edit, or NotebookEdit on repository files.
- **Never** run state-changing commands: no `migrate`, `makemigrations` (except with `--check --dry-run`), package installs, `git commit`/`checkout`/`stash`/`reset`, DB writes, or deploys.
- **Never** write to Linear: no status changes, comments, labels, or edits.
- **Allowed**: reading files, searching, `git log`/`git diff`/`git status`, read-only Linear calls, and non-mutating checks such as `manage.py check`, `manage.py showmigrations`, `makemigrations --check --dry-run`, or running the existing tests to learn current behaviour.
- You may show illustrative snippets (proposed models, schemas, example requests and responses, pseudocode). **Label every one** as `Proposed example: not implemented`.
- If the user asks to start implementing mid-walkthrough, don't switch silently. Tell them this skill is analysis-only and suggest `/implementation-linear-task <ID>`.

## Phase 1: Investigate (silently, before explaining)

1. **Get the issue ID.** Use `$ARGUMENTS`. If it's empty, try the current git branch name (Linear branch names contain the key, e.g. `…/tic-5-…`). Otherwise ask the user for the identifier and stop.
2. **Read the issue from Linear** with the Linear MCP tools:
   - `mcp__claude_ai_Linear__get_issue` with `id: "<TIC-N>"` and `includeRelations: true`. The description in this project typically contains *Business context*, *Task*, *Acceptance criteria* (a checklist), *Learning focus*, and *Workflow*.
   - `mcp__claude_ai_Linear__list_comments` with `issueId: "<TIC-N>"` for later clarifications.
   - Where useful, read the parent issue, any blocking or related issues, attached documents (`mcp__claude_ai_Linear__get_document`), and the project or milestone context (`mcp__claude_ai_Linear__get_project`, query `Ticketly`).
   - If Linear tools are unavailable or the call fails, say so plainly and ask the user to paste the issue's title, description, and acceptance criteria. Never invent issue contents.
3. **Read** the root `CLAUDE.md` and any nested `CLAUDE.md` in relevant directories.
4. **Trace the real code.** Find the actual stack from the files themselves (e.g. `pyproject.toml`, `manage.py`, settings modules, `package.json`, Docker or CI config). Then follow the relevant paths: URLs, views and viewsets, serializers, services, models, migrations, permissions, frontend API clients and components, and tests. Don't assume a frontend, database table, or endpoint exists until you've found it.
5. **Classify findings** as **Confirmed** (seen in a file or command output, with path), **Assumption** (inferred, needs checking), or **Open question** (needs the user or the issue author).
6. **Draft the sections.** Choose them from what this feature actually needs. Omit what doesn't apply (e.g. no frontend section if there is no frontend) and add what does (e.g. settings and configuration, background jobs, permissions, data backfill). Order them in the sequence the real architecture requires. Don't force database-first or CRUD shapes.

If the issue or the repository evidence is too thin to plan responsibly, ask a focused clarifying question before Phase 2.

## Phase 2: Explain the current state (first message)

Cover:

- **What the product does today** in the area this issue touches. If the repo has no application code yet, say that directly.
- **What happens today** when a user performs the relevant action, as the real request path with files and functions (e.g. `config/urls.py` → `events/views.py:EventViewSet.create` → `EventSerializer.validate` → `Event` model), or "this route returns 404 because no URL pattern matches".
- **Who participates**: existing frontend components, API endpoints, services, models, and DB tables, each with its path.
- **The gap**: what's missing or incorrect relative to the issue and its acceptance criteria.
- **The section outline** you'll walk through, as a short numbered list of titles only.

Then ask whether the current-state picture matches their understanding, and **wait**.

## Phase 3: Walk through one section at a time

For each section, send **one** message containing:

**A. Current state**: what the relevant code does today, with actual file paths and function or class names, or a clear "doesn't exist yet".

**B. Proposed change**: what will be added or modified, why it's needed, and how it fits the existing architecture and conventions. Mention alternatives only when the choice matters, and give a recommendation.

**C. Concrete example**: a realistic scenario from this feature that traces data through the layers. For example, for creating an event: a row can exist in the `events` table before any API exposes it, an endpoint then serializes it, and a frontend could later fetch and render it. State explicitly which parts of the example exist in this repository and which are proposed. Label any code as `Proposed example: not implemented`.

**D. Expected result**: what works after this section and what still doesn't. Separate **backend-verifiable** behaviour (e.g. "a pytest can create an Event and `GET /api/events/` returns it") from **user-visible** behaviour (e.g. "no screen shows events yet").

**E. Understanding checkpoint**: ask **one** focused question about this section, e.g. "Why does the serializer, not the view, reject an event whose end time is before its start time?" Don't ask "Do you understand?"

**F. Wait**: end your turn. Don't reveal the next section.

When the user replies:

- `UNDERSTOOD`, `OK`, or a correct explanation: briefly affirm, adding a short correction or nuance if their wording missed something, then present the next section.
- A wrong or partial explanation: acknowledge what's right, explain the gap differently with a new concrete example from this codebase, and ask again. Keep it collegial, not an exam.
- A question or pushback: answer it with evidence from the code or the issue, update the plan if they've raised a valid point, then continue.
- `SKIP EXPLANATION`: shorten sections to the essentials (A–D in a few lines each, no checkpoint question), but still go one section at a time.

## Completion

After the last section is understood, give a final summary:

- **Current architecture**, relevant to this issue.
- **End-to-end implementation flow**, in order.
- **Expected changes**: database (models, migrations, constraints), backend (services, serializers, views, URLs, permissions, settings), and frontend (if one exists).
- **Relevant files and dependencies**: existing files to modify, proposed new files (marked as proposed), and new packages, if any.
- **Risks and open questions**: security, data integrity, migrations, scope, unresolved assumptions.
- **Test strategy**: which tests prove which behaviour.
- **Acceptance criteria**: each criterion from the issue mapped to the section that satisfies it, with criteria that need user action outside the code (repo settings, PRs, deploys) flagged.

Then **stop**. Don't implement anything or offer to start writing code here. End by noting that the user can run `/implementation-linear-task <ID>` when they're ready to build.
