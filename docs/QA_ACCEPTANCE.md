# REN — QA & Acceptance Criteria

## Global rule

No task is complete merely because an asset/script exists.

A task is complete when its acceptance criteria are satisfied or explicitly marked `LOCAL_VALIDATION_REQUIRED`.

## Greybox acceptance

- player spawns inside intended space
- no spawn inside collision
- intended route is traversable
- side branch is accessible
- exit is reachable
- player cannot trivially fall through world
- scale feels plausible in third person
- no unintended duplicate generated actors

## Interaction acceptance

- one E press causes one interaction
- trace does not fire repeatedly from a held key unless designed
- self is ignored
- non-interactable Actors fail safely
- interactable receives correct Interactor
- prompt appears/disappears predictably
- range feels usable, not pixel-perfect

## No-shadow acceptance

Before Sheut recovery:
- Nefer has no projected human shadow
- nearby props do cast shadows
- lighting clue is readable in gameplay
- removal does not create distracting rendering artifacts
- state survives camera changes

## Door acceptance

- opens only from valid interaction/state
- collision updates correctly
- player cannot become trapped
- animation has believable mass
- world transform/end state is deterministic

## Boss acceptance

Face-Eater:
- silhouette remains readable
- no geometry/identity redesign during gameplay
- attacks telegraph
- hitboxes match animation reasonably
- state transitions are deterministic
- exposed state is visually obvious
- completion cannot soft-lock the level

## Spatial continuity acceptance

After layout lock:
- world-lock validation has no unexplained transform drift
- permanent damage/state is consistent
- camera changes do not require environment relocation
- left/right relationships remain stable

## Cinematic acceptance

- entry world position matches gameplay
- exit world position matches return to gameplay
- no player teleport without explicit transition
- no visible level pop/rebuild
- shot has one clear visual purpose
- cinematic does not obscure required gameplay readability

## Performance acceptance

Do not optimize before profiling.

For vertical slice, gather:
- frame-time snapshot in Tomb
- frame-time snapshot in Necropolis reveal
- frame-time snapshot during Face-Eater encounter

Document hardware and scalability settings when profiling.

## Cloud acceptance

A cloud task that requires Unreal execution must say:
`LOCAL_VALIDATION_REQUIRED`

Cloud Claude must never claim an Editor test passed if it did not run the Editor.
