# Project Manager Status — Swords and Serpents

Last refreshed: 2026-08-04 15:02 EDT

PROJECT_MANAGER_STATUS
Project: Swords and Serpents
Phase: Native JS/TypeScript port with ROM-verified renderer and gameplay
Milestone: Preserve validated toroidal-world port while resolving remaining fidelity and build-environment risks
Health: 50/65 — Attention
Since last cycle:
- Initial PM evidence refresh completed on 2026-08-04.
- No git repo; progress inferred from README, docs, src/main.ts, assets, and package files.
Blockers:
- Build environment on WSL is blocked by missing `@rolldown/binding-linux-x64-gnu` native dependency.
Risks:
- Decoding/render evidence is strong for Room 0 and documented, but playable full-dungeon behavior and combat rules still need ROM-backed verification beyond the captured first level.
Recommended next actions:
1. Resolve or vendor the missing rolldown native dependency on WSL so `npm run build` can be validated.
2. Expand jzIntv memory captures for additional rooms/levels and compare against current `assets/world_level*.json` outputs.
3. Add deterministic regression checks for BACKTAB/GRAM decode and toroidal movement before changing render logic.
Evidence checked:
- Filesystem: `README.md`, `package.json`, `docs/HANDOVER.md`, `docs/PORT_RUNBOOK.md`, `docs/JZINTV_MEMORY_RUNBOOK.md`, `docs/backtab_pipeline_analysis.md`, `docs/maze_tileset_map.md`, `docs/room0_decode_findings.md`, `src/main.ts`, `vite.config.ts`, `assets/world_level*.json`
