# REN — Performance and Polish Budget (pre-alpha)

Goal: **smooth third-person gameplay with stable frame pacing.** The practical target is about **60 FPS (≈16.7 ms frame time) where achievable** on the user's development machine. Gameplay readability always beats cinematic effects.

- **No hardware claims:** this document makes none. All numbers are measured locally and recorded with the hardware and settings used.
- **Lightweight profiling only:** this is a sprint, so the budget is about 30 min on Day 6 and 20 min on Day 7.

## 1. Measurement rules

- Measure in **Standalone Game** (Editor → Play → Standalone) or, better, the **packaged Development build**. PIE numbers include Editor overhead and are indicative only.
- Record these once per session:
  - CPU, GPU, RAM, OS (the user fills these in)
  - resolution and window mode
  - scalability level (`Settings → Engine Scalability`, or `sg.*` values)
  - RHI (DX12, per `DefaultEngine.ini`)
  - hardware ray tracing on/off (the project currently has `r.RayTracing=True`)
- During measurement, turn VSync off and uncap the frame rate: `r.VSync 0`, `t.MaxFPS 0`. Restore them afterwards.
- Stand still at each capture point for 10 s, then walk the local route for 20 s, and note the worst spikes.

## 2. Tools and commands (built-in, lightweight)

| Command / tool | Use |
|---|---|
| `stat fps` | Frame rate |
| `stat unit` | **Frame**, **Game** (game thread), **Draw** (render thread), **GPU** times in ms |
| `stat unitgraph` | Spot hitches and frame-time spikes over time |
| `stat gpu` | GPU cost by pass (shadows, Lumen, base pass, post) |
| `ProfileGPU` (or Ctrl+Shift+,) | A one-off detailed GPU breakdown of one frame |
| Unreal Insights (`-trace=default` on a Standalone/packaged run) | Only if a hitch can't be explained with the stat commands |

## 3. Capture points (use the same camera direction each time; facing +Y unless noted)

| ID | Area | Position (approx.) | Situation |
|---|---|---|---|
| P-T1 | Tomb burial chamber | (0, −250, 0) | Spawn view, sarcophagus ahead |
| P-T2 | Tomb shadow zone | (0, 900, 0) | Shadow-test light, props and Nefer in view |
| P-N1 | Necropolis reveal | (0, 2850, 0) on the ledge | The whole skyline: towers, gate, bridge |
| P-N2 | Anubis bridge | (0, 4300, 0) | Bridge, both towers, Anubis |
| P-C1 | First combat | Gate court (0, 6800, 0) | **2 Nameless Dead active, fighting** |
| P-F1 | Face-Eater arena | Arena (0, 9000, 0) | **Boss in Combat, attacking** |
| P-F2 | Face-Eater Exposed | near the boss | Seal open, player attacking |

## 4. Record template (one row per capture; keep in `docs/DEVLOG.md` or a perf section of the QA results)

| Date | Build (PIE/Standalone/Packaged) | Capture | FPS | Frame ms | Game ms | Draw ms | GPU ms | Worst spike ms | Notes |
|---|---|---|---|---|---|---|---|---|---|

Reading the numbers:
- **Green:** frame ≤ 16.7 ms.
- **Amber:** 16.7–33 ms.
- **Red:** > 33 ms, or any recurring spike > 50 ms during gameplay.
- The **highest of Game, Draw and GPU** is the bottleneck. Fix that one first.

## 5. If performance is bad — priority order

1. **Severe gameplay hitches and frame-time spikes** (loading or spawning during combat, Blueprint ticks, timer storms). These hurt play most.
2. **Expensive shadows and lights.** Overlapping shadow-casting point lights are costly with Virtual Shadow Maps. Shrink attenuation radii; turn off shadows on *fill* lights (never on the no-shadow clue light or its props); reduce the number of shadowed lights per view.
3. **Excessive geometry or material cost** (overdraw, heavy translucency, very dense meshes once art arrives).
4. **VFX** (particle counts, translucency).
5. **Cosmetic polish** (post-process intensity, bloom, fog).

Rules:
- **Don't remove core gameplay functionality** (attacks, triggers, the no-shadow clue, reveal composition) to hit a number.
- **Project-wide rendering changes need user approval:** disabling hardware ray tracing, changing the Lumen/VSM method, or the RHI. Measure the difference first with scalability settings or console variables at runtime, then propose the change.
- Lower **scalability** settings before changing content.
- **Don't** optimise by intuition: measure, change one thing, measure again.

## 6. Polish budget (to keep polish from becoming an unlimited art pass)

| Area | Day-6 timebox | Stop rule |
|---|---|---|
| Gameplay bugs (BLOCKER/HIGH) | as needed, first | Before anything else |
| Combat readability (telegraphs, hit-stop, enemy wind-ups) | 1.5 h | Readable at gameplay distance |
| Camera (distance, collision, arena framing) | 1 h | QA camera rows pass |
| Lighting / readability (exposure, path, silhouettes) | 1.5 h | No crushed blacks; route always readable |
| Hit feedback (shake, hit-stop, nullable sounds) | 45 min | Every hit is felt; no screen-shake spam |
| Essential audio (only if assets exist locally) | 45 min | Hooks only; no sourcing in-session |
| Visual polish (only with reference masters) | remaining time | Never at the expense of the above |
