## Git workflow

Feature branches → `dev` → `staging` → `main`. Never push directly to `main` or `staging`
(both are protected — promotion happens by merging a PR).

- New work: branch from `dev` (`feat/`, `fix/`, `chore/` prefixes)
- When a feature is ready: merge into `dev`
- When `dev` is stable and tested: promote `dev` → `staging`
- Only when `staging` is verified: promote `staging` → `main`

`dev` is the default branch. This overrides the global "push the branch" default in
`~/.claude/CLAUDE.md`.
