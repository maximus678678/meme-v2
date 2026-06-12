# STAR WARS: SHADOW OF THE REPUBLIC — Story Bible

A Choice of Games–style interactive novel set during the Clone Wars
(between Episodes II and III). The player is a Jedi Padawan, field-promoted
in the war's opening months, who may end the war as a Jedi Knight, a
deserter, a war criminal, or a Sith. The galaxy doesn't know the war is a
trap; the player may come to suspect it.

**Tone:** earnest space opera with real moral weight. War stories, not
power fantasy. The dark side is never cartoonish — it is always the
*faster, fairer-seeming* answer. Light side choices should cost something.

## The Player

- Padawan (later Knight/Commander) of Master **Ilara Venn**.
- Name, pronouns (`${they}` etc.), and address (`${sir}`: sir/ma'am/commander)
  chosen in chapter 1. Never assume gender.
- Background chosen in chapter 1, stored as `background`:
  - `"guardian"` — duelist, raised for the front (saber high)
  - `"consular"` — scholar-diplomat (force high)
  - `"sentinel"` — investigator, comfortable in undercities (guile high)

## Stats (see SCHEMA.md for fairmath)

| var | meaning |
|---|---|
| `saber` | lightsaber combat |
| `force` | Force attunement (sense, telekinesis, mind tricks) |
| `command` | tactics, leadership of troops |
| `guile` | deception, streetcraft, intrigue |
| `dark` | 0 = pure light, 100 = consumed. Starts 20. The spine of the game. |
| `master_rel` | bond with Master Ilara Venn |
| `havoc_rel` | loyalty of Captain Havoc and the 117th |
| `joren_rel` | friendship/rivalry with Joren Kade |
| `nyx_rel` | entanglement with Sev'ara Nyx (0 until they meet in ch4) |
| `council_rep` | standing with the Jedi Council |
| `war_score` | how well the player's theater of war is going |

Dark thresholds used across chapters: `dark >= 40` (slipping, whispers),
`dark >= 60` (the Council notices; Nyx believes you're hers), `dark >= 75`
(point of near-no-return; light endings need real sacrifice).

## Cast

- **Master Ilara Venn** — the player's master. Mirialan, dry-witted,
  privately doubts the war serves the Force. Wounded badly in ch1; her
  survival state matters through ch9 (`master_alive`). She is the player's
  conscience — or the authority they grow past.
- **Captain Havoc (CT-7719)** — clone captain of the 117th "Ghost
  Battalion". Blunt, loyal, keeps a tally of every trooper lost. The
  player's window into what the war costs the men bred for it. High
  `havoc_rel` changes Order 66 in ch9.
- **Joren Kade** — fellow Padawan, the player's age. Brilliant, hungry for
  the Council's approval, a step behind or ahead of the player all war.
  Friend, rival, or — on dark paths — the one who comes to bring you in.
- **Sev'ara Nyx** — Dooku's acolyte (Dathomirian, former Jedi youngling the
  Order failed). Recruiter, seducer, true believer that the Jedi are the
  real lie. Introduced striking in ch4, captures the player in ch6.
  Can be killed, redeemed, joined, or surpassed.
- **Senator Carvel Dunne** — Republic senator selling fleet movements to
  the Separatists through shell companies; the thread the player pulls in
  ch5. Charming, plausible, protected.
- Canon figures (Yoda, Mace Windu, Palpatine, Dooku, Grievous) appear in
  brief, plot-adjacent cameos only. Never put dialogue-heavy scenes on
  canon characters; keep them off-screen forces.

## Chapter Outlines & Contracts

Every chapter MUST: be 5,500–8,500 words of prose; reconverge to a single
exit (or defined exits below); read/respect inbound flags; set its listed
outbound flags on EVERY path through.

### Chapter 1 — "Fires of Jabiim" (char-gen + prologue)
Mud-world meatgrinder. Opens mid-battle as a Padawan beside Master Venn.
Name input, pronoun choice, background choice woven into the action (e.g.
how you fight, what the troopers call you). Venn is gravely wounded
covering a retreat; the player takes field command. Closing scene: a
holo-summons — the Council, short of Knights, grants a field commission.
**Sets:** `background`, pronoun vars, `sir`, initial skill boosts (chosen
background ~50, others ~30), `master_alive true` (she lives, but is in a
bacta coma — ambiguous recovery), first `dark` movement (mercy vs. wrath
on a wounded Separatist officer).
**Exit:** `goto_chapter: 2`.

### Chapter 2 — "The Ghost Battalion"
First command: the 117th, Captain Havoc. Relief mission to the besieged
city of Calden Spire on Pellior — Separatists using a civilian district as
a shield for their droid foundry. Core dilemma: bombard (fast, saves
troopers, kills civilians), infiltrate (risky, tests skills), or siege
(slow, war_score suffers, troopers die in trickles). Havoc judges quietly.
**Sets:** `bombarded` (true/false), `civvies_saved` (true/false),
`war_score` movement, big `havoc_rel` movement.
**Exit:** `goto_chapter: 3`.

### Chapter 3 — "The Neutral World"
Diplomacy on Vethari Prime, a mid-rim shipyard world courting both sides.
Joren Kade is the other Republic envoy — first reunion since Jabiim. A
Separatist delegation (Nyx is *behind* it, unseen) runs sabotage and
frame-jobs. Paths: honest diplomacy (force/command), counter-intrigue
(guile), or strong-arm (saber/dark). The world's allegiance is decided.
**Sets:** `vethari` = `"republic"`, `"separatist"`, or `"burned"` (talks
collapse / player torched the deal), `joren_rel` movement.
**Exit:** `goto_chapter: 4`.

### Chapter 4 — "The Sith Relic"
The Council sends player + Joren to recover a Sith holocron from a tomb
world before Dooku's agents do. Whispers in the dark; the tomb tests each
stat. **Sev'ara Nyx introduced** — she beats them to the inner vault, duel
and verbal seduction ("ask yourself why your Council wants a Sith's
teaching locked away, not destroyed"). She escapes (or is driven off).
Player chooses: surrender the holocron to the Council, or secretly keep it.
**Sets:** `nyx_rel` (first movement, ~10–35), `holocron` = `"council"` or
`"kept"`, dark movements. If `holocron == "kept"`, dark whispers recur in
ch5–8 text segments.
**Exit:** `goto_chapter: 5`.

### Chapter 5 — "The Traitor's Web"
Coruscant. Fleet ambushes keep landing on the player's battle group; the
trail leads to Senator Carvel Dunne. Investigation chapter (guile shines,
but all stats have routes). The catch: exposing Dunne cleanly requires
implicating a friendly admiral Havoc reveres; quiet options include
blackmail (dark, lucrative `war_score`) or summary vengeance (very dark).
Master Venn (if `master_alive`) wakes mid-chapter — holo-call where she
senses what the player is becoming; on kept-holocron paths she *almost*
finds out.
**Sets:** `dunne` = `"exposed"`, `"blackmailed"`, `"dead"`, or
`"escaped"`, `council_rep` movement, `master_rel` movement.
**Exit:** `goto_chapter: 6`.

### Chapter 6 — "In Chains"
The ambush the traitor's intel bought: player's cruiser taken, player
captured. Weeks in Nyx's custody aboard the *Penumbral*. No torture
porn — the chapter is a seduction: Nyx shows the player true things
(Jedi hypocrisies, the war's casualties, her own scars) wrapped around
the lie. Escape attempts test skills; Havoc mounts an unsanctioned rescue
if `havoc_rel >= 65`. The player leaves by: escaping alone, being rescued,
*or walking out at Nyx's side*.
**Sets:** `joined_nyx` (true/false), `nyx_rel` large movement, dark
movement (this chapter should be the biggest dark swing in the game),
`escaped_how` = `"alone"`, `"havoc"`, `"nyx"`.
**Exit:** `goto_chapter: 7`.

### Chapter 7 — "The Crossroads"
The paths harden. THREE strands sharing one chapter file:
- **Light/loyal** (`not joined_nyx`, `dark < 60`): debrief, suspicion,
  cleared for the Outer Rim Sieges; rebuild trust with Havoc/Joren/Venn.
- **Slipping** (`not joined_nyx`, `dark >= 60`): the Council assigns Joren
  to *watch* the player; secret use of the holocron; a war crime
  opportunity that `war_score` rewards.
- **Fallen** (`joined_nyx`): operating as Nyx's partner; tasked to raid a
  Republic medical convoy — first irreversible act, or first betrayal of
  Nyx (double-agent route: `set double_agent true`).
**Sets:** `double_agent` (true/false), relationship swings, `path` =
`"loyal"`, `"slipping"`, `"fallen"` (set from the strand actually played).
**Exit:** `goto_chapter: 8`.

### Chapter 8 — "The Reckoning"
The Siege of Vethari Prime (callback: its allegiance from ch3 shapes the
battlefield). All strands collide: Dooku commits Nyx; the Republic commits
the player's group, Joren, and (if recovered) Master Venn. Climactic
confrontations resolve here: final duel or final mercy with Nyx
(`nyx_fate` = `"dead"`, `"redeemed"`, `"victorious"`, `"fled"`), Joren
lives or dies (`joren_alive`), Venn lives or dies if she was alive
(`master_alive` may flip false). Fallen players can seize Nyx's place or
overthrow her; double agents get their reveal.
**Sets:** `nyx_fate`, `joren_alive`, final `war_score`/`dark` movements.
**Exit:** `goto_chapter: 9`.

### Chapter 9 — "Order 66" (epilogue + ALL endings)
Months later: the war ends. Order 66 falls on every path differently.
Branch on `path`/`dark`/`joined_nyx`/`havoc_rel`/`nyx_fate` etc. into
**at least 8 endings** (`ending.id` / working titles):
- `ending_knight` — died-with-honor OR survived Order 66 via Havoc's
  warning (`havoc_rel >= 70`): the Knight in exile, hope intact.
- `ending_martyr` — light-side player gunned down beside their troops.
- `ending_exile` — saw the rot, walked away before the end; survives.
- `ending_redeemer` — redeemed Nyx; the two vanish into the Rim together.
- `ending_inquisitor` — dark but obedient: spared, broken, leashed by the
  new Empire.
- `ending_sith` — `dark >= 75`, fallen path: supplants Dooku's place at
  the new Emperor's side... and realizes the leash too late, or not at all.
- `ending_warlord` — fallen but defiant: refuses Palpatine, takes the
  117th (or Nyx's fleet) and burns out as a rogue warlord.
- `ending_gray` — double agent / slipping player who stops at the brink:
  scarred survivor, neither Jedi nor Sith.
Each ending: 400–800 words, personalized by flags (mention Havoc's fate,
Venn, Joren, Vethari, Dunne where relevant).

## Continuity quick-reference (read before writing)

Flags you may READ (set by earlier chapters): `background`, `master_alive`,
`bombarded`, `civvies_saved`, `vethari`, `holocron`, `nyx_rel`, `dunne`,
`joined_nyx`, `escaped_how`, `double_agent`, `path`, `nyx_fate`,
`joren_alive`.

The 117th's troopers: Havoc plus named troopers **Dice, Longshot, Tally**
(kill at most one, and only in ch8). The player's cruiser is the
*Resolute Dawn*. Venn's lightsaber is green; the player's is blue unless
dark paths bleed it (mention sparingly). Nyx fights with paired red blades.
