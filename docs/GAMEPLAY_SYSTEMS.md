# REN — Gameplay Systems Specification

## 1. Third-person traversal

Target feel:
- deliberate, grounded
- responsive enough for action combat
- not hyper-acrobatic
- camera readable in narrow tombs and larger Duat spaces

Prototype uses template locomotion until custom movement is justified.

## 2. Interaction

### User action
Press `E` / `IA_Interact`.

### Trace
- from gameplay camera
- forward
- ~350 cm beyond the player's position along the camera ray (start projected to the pawn; see `docs/tasks/P1_INTERACTION_FOUNDATION.md`)
- sphere trace ~30 cm radius
- ignore self
- Visibility or dedicated interaction channel after prototype

### Interaction behavior
The player should never need pixel-perfect aiming at large interactables.

First interactions:
- Blank Cartouche
- Sarcophagus
- Exit Door
- Glyph Mechanism

### Prompt
Prototype:
- small contextual `E — Interact`
- object-specific label only if needed

Avoid over-tutorializing.

## 3. No-shadow / Sheut state

Before Sheut recovery:
- Nefer casts no projected human shadow
- contact darkening is acceptable
- props/environment still cast shadows

This mechanic must be visible in designed lighting, not merely technically enabled.

For the slice:
- use a controlled clue zone with fixed light
- ensure nearby column/jars/pedestal cast readable shadows
- Nefer does not

Do not fake the clue by moving the world or changing the light per camera.

## 4. Reed Blade

Design:
- ritual scribal weapon
- fast enough for readable action
- physically grounded
- not generic fantasy sword behavior

Prototype combat:
- light attack chain
- one heavier commitment attack only if needed
- dodge
- hit reaction
- enemy damage
- boss damage gate

Do not create a large combo tree for the slice.

## 5. Heka / Glyph interaction

Heka should feel like writing changes reality.

Slice mechanic:
- player possesses or acquires a specific Glyph
- glyph interacts with a pre-authored mechanism
- existing carved grooves respond
- stone/ink/mechanism changes physically

No generic "magic blast."

## 6. Face-Eater encounter

Core fantasy:
an entity that consumes / steals identity.

Visual tells:
- empty cartouche head
- embedded identity fragments
- hooked/extraction staff

Prototype attack set:
1. horizontal hook sweep
2. vertical/diagonal heavy strike
3. grab attempt
4. short recovery window

Slice mechanic:
- normal attacks alone are insufficient or inefficient
- player creates an opening
- Glyph interaction exposes chest seal
- boss enters Exposed state
- player damages vulnerable identity mechanism

Boss must not morph into unrelated forms.

## 7. Death / restart

Prototype:
- reload encounter or checkpoint
- fast restart
- no elaborate death meta-system yet

## 8. Camera

Gameplay:
- 3–5m behind player depending on space
- restrained FOV
- little/no cinematic depth of field
- stable exposure
- readable level

Cinematics:
- use Sequencer
- preserve same world
- return quickly to gameplay control

## 9. Audio priorities

First-pass important sounds:
- footsteps on stone
- cloth
- sarcophagus stone/wood friction
- reed/papyrus
- door mass
- subtle funerary ambience
- boss staff impact
- whispers used sparingly

Avoid making the audio identity depend on stereotypical "Egyptian" instrumentation.
