# REN — Build / Release Checklist (shareable pre-alpha)

Scope: one **shareable Win64 pre-alpha build**. This is **not** a distribution or store pipeline: no signing, installers, store depots or crash-reporting backend.
Run on Day 7 after feature freeze and QA (`docs/tasks/MASTER_LOCAL_EXECUTION_ORDER.md` §9). Tick every box. A box that can't be ticked is logged in `docs/BUG_TRIAGE.md` with a severity.

## A. Source state

- [ ] `git status` is clean. The current commit is pushed. Note the commit hash: `________`.
- [ ] `git lfs pull` done. No `.uasset`/`.umap` file is an LFS pointer (open one map and one character in the Editor; they load).
- [ ] No open BLOCKER or HIGH in `docs/BUG_TRIAGE.md` (or each HIGH is accepted by the user in DEVLOG).
- [ ] World-lock: `REN_Validate_WorldLock.py` run on Tomb, Necropolis and GateWest standalone. Reports committed. No unexplained spatial failures.
- [ ] Editor: **Compile all Blueprints** (e.g. File → Validate Assets / open each REN Blueprint). **0 compile errors.**
- [ ] No Blueprint references assets under `/Game/Variant_Combat/` that were modified (`git status` shows no template changes).

## B. Project settings

- [ ] Maps & Modes: **Game Default Map = `L_REN_Slice`**; Editor Startup Map = `L_REN_Slice`. The GameMode override resolves to `BP_REN_GameMode`.
- [ ] Packaging → **List of maps to include**: `L_REN_Slice`, `L_Tomb_Blockout`, `L_Necropolis_Blockout`, `L_GateWest_Blockout`.
- [ ] Packaging → Build Configuration: **Development** (first build is Development; Shipping is out of scope).
- [ ] Debug aids for players are off: `bDebugTelegraphs` (boss) **off** in the shipped level instance (or kept only if the user decides it helps readability; record the decision); no debug keys (QA H4); no print-string spam on screen.
- [ ] Placeholder/editor labels (`TEMP_PLACEHOLDER` TextRenders) are **Hidden in Game** and not visible in the build.

## C. Package

- [ ] Platforms → Windows → **Package Project** to a folder **outside the repository** (e.g. `..\REN_Builds\PreAlpha_<date>\`). **Never commit packaged output.**
- [ ] The packaging log shows no errors. Note any warnings about missing assets/redirectors in BUG_TRIAGE.

## D. Smoke test the packaged build (Editor closed)

- [ ] Launches **without the Editor** on the dev machine. If possible, also on a second machine.
- [ ] Starts in the **Tomb** at `REN_PlayerStart` with control on the first frame.
- [ ] **Keyboard + mouse** sanity: move, look, interact (E), attack, dodge (if present), menu/quit.
- [ ] **Controller** sanity (if a gamepad is available): the same actions on their mapped buttons; no dead inputs.
- [ ] **Arabic subtitles** render connected and right-to-left (Cartouche, shadow line, side clue, Anubis).
- [ ] Complete run: Tomb → Necropolis → Anubis → Gate → first combat → Face-Eater **defeat** → reward beat → **end card**. Record the total time.
- [ ] **Restart test:** die in the first combat and in the Face-Eater fight (×2 each). The checkpoint restart is correct, and there are no duplicate enemies or boss.
- [ ] **Face-Eater defeat:** the entrance unlocks, the bar disappears, the end card appears.
- [ ] No missing-asset checkerboards / default-grey surprises where final placeholders were expected. No obvious debug text on screen.
- [ ] Performance capture on the packaged build (`docs/PERFORMANCE_AND_POLISH_BUDGET.md` P-T2, P-N1, P-C1, P-F1) recorded.
- [ ] **Quit / relaunch:** quit from the end card (or the menu); relaunch; it starts correctly at the Tomb again (no stale state).
- [ ] Logs: check the packaged `Saved/Logs` for `Accessed None`, `Error`, `Ensure`. Log any found in BUG_TRIAGE.

## E. Release notes (short; put them in DEVLOG and alongside the build folder)

- [ ] Build date, commit hash, configuration, measured playtime.
- [ ] Controls.
- [ ] **Known issues** (MEDIUM/LOW Won't-fix, accepted HIGHs).
- [ ] Statement: *"Pre-alpha. Greybox environments and `TEMP_PLACEHOLDER` characters; not visual authority."*
- [ ] `build: prepare pre-alpha package` committed (docs, reports and notes only).
