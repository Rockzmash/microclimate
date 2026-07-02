## Git workflow

Feature branches → `dev` → `staging` → `main`. GitHub enforcement is not enabled on this private repo (free plan); the ladder is held by convention + the orchestrator governor's branch-precondition. Do not push to `main`/`staging` directly.

- New work: branch from `dev` (`feat/`, `fix/`, `chore/` prefixes)
- When a feature is ready: merge into `dev`
- When `dev` is stable and tested: promote `dev` → `staging`
- Only when `staging` is verified: promote `staging` → `main`

`dev` is the default branch. This overrides the global "push the branch" default in
`~/.claude/CLAUDE.md`.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
