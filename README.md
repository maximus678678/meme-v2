# STAR WARS: Shadow of the Republic

*A Clone Wars interactive novel in the style of Choice of Games.*

You are a Jedi Padawan, field-promoted in the opening months of the Clone
Wars. Over nine chapters you will command clone troopers, negotiate for
worlds, hunt Sith relics, unmask a traitor in the Senate, and face a
seduction to the dark side that is never cartoonish — only ever the
faster, fairer-seeming answer. End the war as a Knight, a deserter, a
warlord, an Inquisitor, or a Sith. Order 66 falls on every path
differently.

A single playthrough runs roughly 2–3 hours; seeing the major paths
(light, dark, and the gray roads between) takes 5+.

## Play

Requires only Python 3 (no dependencies):

```
python3 play.py
```

At any choice prompt you can also type `stats`, `save`, `load`, or `quit`.
The game autosaves to `savegame.json` continuously, so you can quit and
pick up where you left off.

## Design

Built in the Choice of Games house style:

- **Second person, present tense** prose; choices express who your
  character *is*, not puzzle-guessing.
- **Opposed and fairmath stats** — Lightsaber, Force, Command, Guile, a
  Light/Dark alignment meter, and relationship scores that gate scenes
  and endings. High stats get harder to raise (fairmath), so builds
  matter.
- **Branch-and-bottleneck structure** — chapters branch widely and
  reconverge, carrying flags forward; early choices (a bombarded city, a
  holocron you didn't turn in) echo through to the epilogue.
- **8 endings**, personalized by the state of your war, your battalion,
  and the people you saved or broke along the way.

## Project layout

| path | what |
|---|---|
| `play.py` | entry point |
| `engine/` | scene-graph engine: stats, fairmath, conditions, saves |
| `scenes/chapter0N.json` | the story, one file per chapter |
| `tools/validate.py` | checks scene files (links, syntax, word counts) |
| `tools/simulate.py` | random-walk playtester: coverage + ending reachability |
| `SCHEMA.md` | scene file format and house-style rules |
| `STORY_BIBLE.md` | cast, stats, chapter contracts |

This is a non-commercial fan work. Star Wars and all related properties
belong to Lucasfilm/Disney.
