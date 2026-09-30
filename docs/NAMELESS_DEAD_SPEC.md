# REN — Nameless Dead: Vertical-Slice Spec

Status: direction **locked by user decision on 2026-09-30**. Scope: one enemy family for the 7-day pre-alpha (Beat 7.5, 16–22 min, polish tier C).

## 1. What they are

Real ancient Egyptian people whose individual identity is being erased. They are the Unname's work in miniature: people becoming unrecorded.

The tragedy must survive combat. They can fight aggressively, but they must *read* as frightened, grieving people, not monsters.

## 2. Visual rules

**Must:**
- Look like a recognisable human with human anatomy.
- Warm-brown Egyptian skin.
- Normal dark human eyes.
- Historically grounded, simple linen: kilt, sheath dress or shawl; worn and plain.
- Show a *subtle* loss of personal individuality.

**Must not look like:**
- zombie, ghost, mummy monster or generic undead
- a grey corpse
- a faceless creature
- anything with glowing eyes
- skull imagery
- rotting flesh
- bandage-monster styling

**Identity-erasure details** (target art; use one or two per individual, never all):
- a scar fading away
- eyebrow asymmetry becoming unnaturally even
- lip asymmetry reducing
- distinctive cheek or ear details becoming generic

The effect is that the faces drift toward *sameness*. A viewer should feel "something is wrong with these people" before they can say why.

## 3. Emotion and body language

- They feel confusion, fear, grief and desperation. There is **no** roaring and no rage-monster posing.
- Signature gesture: some reach toward another person's **face**, including Nefer's, as though trying to remember what a person is.
- Movement:
  - Hesitant approach (walk speed is lower than the template enemy).
  - Committed but clumsy attacks, like grasping and shoving, not martial-arts combos.
  - Brief stillness after being hit, as if the pain were a memory.

## 4. Sprint implementation (placeholder; one week)

**Asset:**
- `/Game/REN/Characters/Enemies/NamelessDead/BP_NamelessDead`, a REN-owned duplicate of `/Game/Variant_Combat/Blueprints/AI/BP_CombatEnemy`. Run the donor audit first (see `docs/SPRINT_7DAY.md`).
- Mesh: the template Manny/Quinn mannequin, with a **REN-owned material instance duplicate**:
  - skin: warm-brown tint
  - body: a flat linen off-white/sand colour where the mesh allows
  - **never the default grey**
  - no emissive
- No custom modelling this week. Final human models are out of sprint scope.

**Behaviour** (reuse the template StateTree; tune only numbers):
- Lower walk speed.
- Longer attack wind-up, for readable telegraphs in tier C.
- Low health, so 2–4 light combos kill one.
- Moderate damage.
- At most **3 active at once**.

**The face-reach**, cut-able (it sits near the top of the cut order):
- Either a simple reach montage, or reuse the template attack montage at reduced play-rate while the enemy is still out of attack range.
- If no suitable animation exists in the template set, cut it this week. Don't build an animation pipeline for it.

**Defeat:**
- The body collapses (ragdoll or the template death) and stays still. No explosion, no dissolve VFX, no loot drop.
- Optional one-line whisper SFX: a *fragment* of a name that never finishes. Placeholder audio is OK.

**Audio placeholders:** breath, linen movement, stifled weeping, murmured half-names. Avoid monster growls.

## 5. Encounters (numbers for P3; layout in the GateWest spec)

- Encounter 1 teaches the combo and dodge: 2 Nameless Dead.
- Encounter 2 is optional (cut order #2): 3 Nameless Dead, arriving staggered.
- A checkpoint (`BP_Combat_CheckpointVolume` duplicate or equivalent) goes before each encounter. Death returns the player there quickly.

## 6. Acceptance (tier C)

- They never read as zombies, ghosts or mummies in a screenshot. Review a PIE screenshot against section 2.
- No grey-skin default material is visible.
- The player can always tell who is about to attack, from wind-up plus approach.
- A fight never soft-locks: all enemies can be killed and restart works.
- No more than 3 are active at once.

## 7. Out of scope

Variants or families beyond this one, unique facial rigs, morph-target identity erasure (art pass later), dialogue, lore codex, loot, and spawning systems beyond the template spawner.
