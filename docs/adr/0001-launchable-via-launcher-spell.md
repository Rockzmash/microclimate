# ADR 0001: Launchable via the workshop launcher spell

**Status:** Accepted
**Date:** 2026-07-06
**Deciders:** David

## Context

This repo runs a localhost dev server. It is registered in the **workshop `launch` spell**
(`~/dev/workshop/spells/launch/projects.yaml`) so it can be started and opened in the browser
with one press — from the Sobo cockpit's grimoire (a shell spell) and a Stream Deck key.

How the launcher works (see `~/dev/workshop/docs/design-specs/2026-07-06-launcher-spell-design.md`):

- It runs `cd <run-dir> && <start>` on **whatever branch is checked out** — it does not pin a
  branch or commit, so it always runs current code (dev servers hot-reload live edits).
- It **auto-detects** the port the server actually listens on and opens that, so a dev-server
  **port change on any branch does not break launching**.
- It hardcodes, in the central registry, four things that are *not* the app's code logic and so
  can silently drift out of sync: this repo's **run directory**, **start command**, **browser URL
  (host + path)**, and a **port hint**.

## Decision

This repo commits to being launchable under that contract, with these values:

- **Run directory:** `proxy` (relative to the repo root)
- **Start command:** `.venv/bin/python server.py`
- **Browser URL:** `http://localhost:8770`
- **Port hint:** `8770` (auto-detected at runtime; kept unique across all launcher projects)

> Runs from `proxy/` under a WSL venv (`uv venv` + `uv pip install -r requirements.txt`).

Rules this repo follows so the launcher stays correct:

1. If we change the **start command**, the **served URL path**, or **move the run directory**,
   we update `~/dev/workshop/spells/launch/projects.yaml` **in the same change**.
2. A **port-only change needs no registry edit** — the launcher auto-detects it — but updating
   the hint keeps multi-server disambiguation accurate.
3. We keep the dev server **runnable from a clean checkout** (the start command works after the
   documented install step); the launcher does **not** run installs.
4. The port stays **unique** across the shared launcher map (see the registry header).

## Consequences

- One-press launch stays consistent across every `~/dev` localhost app, on any branch.
- A small, explicit **cross-repo coupling**: the workshop registry. Changing this repo's launch
  surface without updating it breaks *this launcher entry* (not the app itself).
- Because every launchable repo carries this same ADR, future changes — in a feature, `dev`,
  `staging`, or `main` branch — inherit the same rules, keeping the launcher up to date.
