# REN — World Space & Continuity Bible

## Absolute principle

**CAMERA MOVES. WORLD DOES NOT.**

The game world is a persistent physical 3D space.

A new shot or camera angle is a new view of the same level, not a redesigned composition.

## Authority

Once a space exists in Unreal:
- Actor transforms in Unreal are authoritative.
- Old concept-image layouts are references only.
- Approximate coordinates in design documents do not override live transforms.

## Locked categories

After layout lock, preserve:
- floors
- walls
- ceilings
- doors
- gates
- stairs
- bridges
- ledges
- pits
- platforms
- shrines
- braziers
- lamps
- jars
- furniture
- carvings
- inscriptions
- cracks
- debris
- ritual props
- water boundaries
- landmarks
- playable paths

## No mirroring

Left and right remain physically defined.

Reverse angles must reveal the same environment from the opposite viewpoint.

Never mirror a level to improve composition.

## Scale lock

Once approved:
- door height
- bridge width
- shrine footprint
- arena size
- weapon length
- character height
- boss height

remain consistent.

## Damage continuity

Damage created by gameplay persists:
- broken column section
- cracked floor
- scorched surface
- moved debris

Later cameras must see the same damage state unless the level is explicitly reset.

## Light-source continuity

Physical lights stay where they are.

Changing camera angle can change screen-space appearance, not light world position.

## Character blocking

For consecutive cinematic/gameplay transitions track:
- character world position
- facing
- weapon state
- pose state
- relevant landmark distance

Do not teleport characters between continuous cuts.

## Tomb opening continuity

Current v3 blockout concept:
- burial chamber with sarcophagus
- Blank Cartouche clue on player-right
- forward corridor
- no-shadow clue zone
- left side clue chamber
- monumental exit
- short transition tunnel
- reveal ledge

The live Unreal transforms supersede this prose.

## Vertical Necropolis continuity

When built, permanently define:
- main route
- first branching bridge
- elevated stairs
- sealed gate
- major void
- suspended sarcophagus clusters
- overhead black river
- star openings below
- Anubis bridge zone

## Solar Barque continuity

When built:
- rear player area
- central combat deck
- Ra shrine forward-center
- left/right bypass
- prow stairs/platform
- Seth prow position
- rowing stations
- fixed braziers/rails/ropes

No mast.
No sail.
No tall rigging.

## World-lock workflow

Before risky level changes:
1. Run `Scripts/Editor/REN_Export_WorldLock.py`.
2. Commit the resulting manifest.
3. Perform the intentional edit.
4. Run `Scripts/Editor/REN_Validate_WorldLock.py`.
5. Review differences.
6. If change is intentional, export again (writes `<World>.worldlock.candidate.json`), promote it to baseline deliberately, and document it in `DEVLOG.md`. See `ProjectDocs/WorldLocks/README.md`.

Never accept unreviewed spatial drift.
