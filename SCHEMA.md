# Scene File Schema

Each chapter is one JSON file: `scenes/chapter01.json` ... `scenes/chapter09.json`.

```json
{
  "chapter": 3,
  "title": "The Neutral World",
  "start": "c3_start",
  "nodes": { "c3_start": { ... }, ... }
}
```

Rules:

- Every node id in the whole game must be unique. Prefix every node in
  chapter N with `cN_` (e.g. `c3_landing`, `c3_senate_2`).
- Every chapter's start node MUST be named `cN_start`.
- To send the player to the next chapter use `"goto_chapter": N` (on a node
  or on a choice) — never `"goto": "c4_start"`.

## Node

```json
{
  "text": "...",                  // string OR list (see Text below)
  "effects": ["dark += 5"],       // optional, applied on entering the node
  "choices": [ ... ],             // optional
  "goto": "c3_next",              // linear continuation (if no choices)
  "goto_chapter": 4,              // OR jump to next chapter
  "input": {"var": "name", "prompt": "What is your name?"},  // free-text input
  "ending": {"id": "ending_sith", "title": "Lord of the Sith"}  // game over
}
```

A node needs exactly one way forward: `choices`, `goto`, `goto_chapter`,
or `ending`. An `input` node also needs a `goto`.

## Text

A string, or a list mixing plain strings and conditional segments. Segments
are joined as separate paragraphs. Use `\n\n` inside strings for paragraph
breaks.

```json
"text": [
  "The gunship shudders through flak.",
  {"if": "havoc_rel >= 60", "text": "Havoc catches your eye. \"With you, ${sir}.\""},
  {"if": "dark >= 50", "text": "The fear in the hold tastes almost sweet."}
]
```

Interpolation: `${name}`, `${they}`, `${them}`, `${their}`, `${theirs}`,
`${sir}` (how clones address you), and `${They}` etc. for capitalized forms.
These refer to the PLAYER. Never hardcode the player's gender.

## Choices

```json
{
  "text": "Hold the line, whatever it costs.",
  "if": "command >= 40 and not retreated",      // optional visibility test
  "effects": ["command %+ 15", "war_score += 10", "set held_line true"],
  "goto": "c2_holdout"
}
```

## Conditions (`if`)

`and`, `or`, `not`, parentheses, `>= <= == != > <`, integers, `true/false`,
quoted strings, variable names. Unset variables read as 0/false.
Examples: `dark >= 60`, `background == "consular"`, `not master_alive`.

## Effects

One operation per string:

- `set flag true` / `set background "guardian"` / `set war_score 50`
- `stat += 10` / `stat -= 10` (clamped 0..100)
- `stat %+ 20` / `stat %- 20` — **fairmath, use this for skills,
  relationships, and dark**: gains shrink as the stat nears 100, losses
  shrink near 0. Typical nudge: 10–20.

## Style rules (Choice of Games house style)

- Second person, present tense, no protagonist dialogue quirks forced on
  the player. "You feel", "You ignite your blade."
- Choices express *who the player is*, not puzzle-guessing. 3–5 options;
  at least one should tempt toward the dark side or a colder pragmatism.
- Skill tests: gate the *outcome*, not the option. Let the player attempt
  bold things; branch on `saber >= 55` etc. inside the next node, or offer
  conditional choices as bonus options.
- Stats move on most choices. Use fairmath. Dark side gains should feel
  seductive and *reasonable* in the moment.
- Branch-and-bottleneck: branches within a chapter reconverge before the
  chapter exit, carrying flags forward instead of parallel plotlines.
- 150–350 words of prose per node. No node should dump more than ~400.

## Validation

Run `python3 tools/validate.py scenes/chapterNN.json` (single-file mode)
until it reports `OK`. Fix every ERROR; take WARNs seriously.
