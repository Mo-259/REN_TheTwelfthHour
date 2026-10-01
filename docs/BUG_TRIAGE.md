# REN — Bug Triage (pre-alpha)

Every bug found in local testing is logged here (§5) with a severity. Severity decides the order of work, not who found it or how interesting it is.

## 1. Severity levels

| Severity | Definition | Examples |
|---|---|---|
| **BLOCKER** | The slice can't be completed, the game crashes, or progress is permanently lost | crash; can't finish the slice; the player falls through the world permanently; Face-Eater soft-lock; respawn broken; an interaction required for progression doesn't work (Exit Door, Glyph slab, Gate, combat gate, arena slab); the arena slab traps or launches the player |
| **HIGH** | Completable, but a core beat or mechanic is broken or unreadable | the boss mechanic becomes unreadable; the no-shadow clue is broken (Nefer casts a shadow, or props don't); the camera makes combat unplayable; a Glyph pillar can't reliably be reached during a window; collision blocks the critical path; Arabic subtitles unreadable; damage numbers clearly wrong (boss unkillable or one-shot) |
| **MEDIUM** | Noticeable quality issue; a workaround exists | visual pop; subtitle timing or overlap; a minor collision snag; a temporary material problem; a light leak; a camera jitter in one spot |
| **LOW** | Cosmetic or non-blocking polish | cosmetic mismatch; placeholder looks rough; a small alignment issue; wording polish |

When unsure between two levels, pick the higher one, then re-assess after reproducing.

## 2. Rules

- **Day 7 rule:** after **feature freeze**, fix **BLOCKER and HIGH first**. **Don't** spend the shipping window on LOW bugs while any BLOCKER or HIGH is open.
- **Day 6 order:** all BLOCKERs → HIGHs → MEDIUMs that touch Tier-A beats (Tomb, Face-Eater) → others.
- **Fixes must not move world-locked geometry** without approval. Validate world-lock after any level fix.
- **Never "fix" by editing template assets** or by adding C++.
- **Retest:** a bug is Fixed only after its repro steps pass in PIE (and in the packaged build for BLOCKER/HIGH found there). Then it's Verified.
- **Won't fix (pre-alpha):** allowed for MEDIUM and LOW, and listed in the release notes as known issues. A BLOCKER can never be Won't fix; HIGH only with the user's written approval in DEVLOG.

## 3. Status flow

`New → Confirmed → In progress → Fixed → Verified` (or `Won't fix (pre-alpha)` / `Cannot reproduce`).

## 4. How to log a bug

Required fields: ID (`BUG-001`…), title, severity, area (Tomb / Necropolis / Gate / Combat / Face-Eater / UI / Build), build (PIE / Standalone / Packaged + commit), repro steps, expected vs actual, frequency (always / sometimes / once), status, fix commit.

## 5. Bug log

| ID | Title | Sev | Area | Build / commit | Repro (short) | Status | Fix commit |
|---|---|---|---|---|---|---|---|
| — | (none logged yet) | | | | | | |
