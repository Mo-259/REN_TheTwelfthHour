# REN — Vertical Slice Specification

## Purpose

Build a 5–10 minute playable proof of concept that demonstrates the unique identity of REN without attempting the full game.

The slice must be strong enough to support:
- gameplay validation
- art-direction validation
- trailer capture
- investor/publisher conversations
- recruitment / team onboarding

## Slice flow

### Beat 1 — Wake
Location: Tomb of No Name.

Player regains control near the sarcophagus.

Goals:
- immediate grounded third-person control
- strong spatial readability
- minimal UI
- no lore dump

### Beat 2 — Identity clue
Player approaches the Blank Cartouche.

Interaction communicates:
- a name should be here
- it has been intentionally erased
- writing and identity are mechanically important

No exposition wall.

### Beat 3 — No-shadow clue
A fixed light source casts readable shadows from props and architecture.

Nefer casts no projected human shadow.

The environment must make this visible without a tutorial pop-up.

### Beat 4 — Side clue chamber
Optional but highly visible side branch.

Purpose:
- reward observation
- introduce environmental storytelling
- hint at Nefer's past / erased names

### Beat 5 — Exit
Player reaches the monumental tomb exit.

Interaction opens the path.

This is the first major authored transition.

### Beat 6 — Vertical Necropolis reveal
Gameplay camera exits into a large impossible Duat space.

The reveal must come from the same persistent level logic:
camera moves; world does not.

Player retains control quickly after reveal.

### Beat 7 — Anubis
Player reaches a long bridge / threshold.

Anubis encounter is controlled and still.

No generic boss posture.

Key function:
- establish stakes around Nefer's missing name
- preserve ambiguity
- direct player toward Gate of the West

### Beat 8 — Gate of the West
Transition from exploration to boss space.

The player sees the arena before combat begins.

### Beat 9 — Face-Eater boss
Boss design:
- ~3.8m funerary humanoid
- empty cartouche as head
- trapped human identity fragments integrated into torso
- extraction/hooked staff
- no skull imagery
- no generic faceless-monster redesign

Core boss mechanic for slice:
1. avoid heavy staff attacks
2. create opening
3. use Glyph/interaction logic to expose chest seal
4. strike / exploit revealed identity mechanism
5. end encounter with Ren-related reward/revelation

Do not overbuild the full boss progression in the first pass.

## Required playable systems

P0:
- third-person movement
- camera
- collision
- stable level

P1:
- interact input
- interaction trace
- interactable convention
- blank cartouche
- exit door

P2:
- no-shadow state
- clue trigger
- simple contextual prompt

P3:
- Reed Blade equip / base attacks
- dodge
- health/damage
- one enemy or boss target

P4:
- Face-Eater state machine
- chest seal mechanic
- boss completion

P5:
- Anubis encounter
- Sequencer / camera polish
- audio pass
- lighting pass

## Out of scope for first slice

- all 12 chapters
- complete progression tree
- full inventory
- crafting
- economy
- open world
- multiple gods as playable encounters
- final Meru/Unname resolution
- shipping save system
- multiplayer
- localization pipeline beyond basic text structure

## Definition of success

A new viewer should understand within the slice:
- this is ancient Egyptian, not generic fantasy
- Nefer is a scribe/dead human, not a god
- names have physical/metaphysical power
- Nefer is missing something essential
- the world is playable and spatially coherent
- the combat can support an action-RPG
- Face-Eater feels unique to REN
