# 🪓 Axe Throwing Scorekeeper

**Welcome to the House of Axe Throwing!!!!** A command-line scorekeeper for two-player axe throwing matches, with an announcer who is *way* too excited about everything.

It tracks every throw, tells you who took each round, and crowns a match winner, following the standard league format used by the International Axe Throwing Federation (IATF). No installs, no dependencies, just Python.

## Quick start

```bash
git clone https://github.com/dmac2electricboogaloo/axe_throwing.git
cd axe_throwing
python3 axe_throwing.py
```

Want Premier rules, where a "touch" Clutch is worth 5 instead of 7?

```bash
python3 axe_throwing.py --premier
```

## How a match works

| Rule | How the app handles it |
|---|---|
| **3 rounds, 5 throws each** | Every round is always played, even if someone has already won two. |
| **Throw values** | `0` (miss or drop), `1` (outer ring), `3` (middle ring), `5` (bullseye). Anything else is rejected and you're asked again. |
| **Clutch** | Only offered on the 5th throw of a round. Each player says whether they call it. A called Clutch scores `7`, or `0` if it misses, because no other area counts once it's called. |
| **Round winner** | The higher point total for the round. Equal totals mean a tied round. |
| **Match winner** | Whoever wins more rounds. One round win plus two ties still wins the match. |
| **Tied on rounds** | A Big Axe sudden-death tiebreaker: one throw each until the scores differ. |
| **Switch lanes** | The app reminds you between rounds. |
| **Total points** | Tracked across all 15 throws and shown on the final scoreboard. |

## Sample session

Typed answers are shown after each prompt. The announcer's intro line is picked at random.

```text
WELCOME TO THE HOUSE OF AXE THROWING!!!!
PLEASE ENTER THE NAME OF THE FIRST PLAYER: ann
PLEASE ENTER THE NAME OF THE SECOND PLAYER: bob
GATHER AROUND BECAUSE IT WILL BE A BLOOD BATH WHEN IT IS:
ANN VERSUS BOB!!!!
ROUND NUMBER 1, THROW NUMBER 1
ANN SCORES A (0, 1, 3, 5): 3
BOB SCORES A (0, 1, 3, 5): 1
The score is ANN 3
The score is BOB 1
...
ROUND NUMBER 1, THROW NUMBER 5
FINAL AXE OF THE ROUND! PLAYERS, CONFER ON YOUR CALLS.
DOES ANN CALL CLUTCH? (Y/N): Y
DOES BOB CALL CLUTCH? (Y/N): N
ANN SCORES A (0, 7): 7
BOB SCORES A (0, 1, 3, 5): 3
The score is ANN 19
The score is BOB 13
ANN TAKES THE ROUND!!!
SWITCH LANES!
...

FINAL SCOREBOARD
ROUND 1: ANN 19 - 13 BOB  (ANN WINS)
ROUND 2: ANN 5 - 15 BOB  (BOB WINS)
ROUND 3: ANN 25 - 5 BOB  (ANN WINS)
ROUNDS WON:   ANN 2 - 1 BOB
TOTAL POINTS: ANN 49 - 33 BOB
AND THE WINNER IS: ANN!!!
```

## Running the tests

```bash
python3 -m unittest -v
```

The tests cover the scoring rules, input validation, Clutch handling, Premier rules, and complete simulated matches, including the Big Axe tiebreaker.

## What's in here

| File | Purpose |
|---|---|
| `axe_throwing.py` | The scorekeeper. The rules live in small functions with no input or output, so they're easy to test. The match flow sits on top of them. |
| `test_axe_throwing.py` | Unit tests and scripted full-match tests. |

## Not covered yet

This is a scorekeeper, so it records what the players and scorekeeper agree on. It doesn't judge throws. A few parts of the full rulebook aren't built in:

- **Clutch during the Big Axe tiebreaker**, which has its own unlock rules (a bullseye first, and more). Tiebreaker throws are limited to `0`, `1`, `3`, and `5`.
- **Final-axe stalemates**, where players can't agree on their calls or throw order.
- **Measuring close throws**, drops, and other judgment calls, which are left to the players and league runner.
- **Saving results** between sessions.

Ideas and pull requests are welcome.

## Disclaimer

This is an unofficial hobby project and isn't affiliated with or endorsed by the IATF. It's based on the IATF's publicly published league rules, so check the official rulebook for the final word. Clutch™ is a registered trademark of BATL Global Corporation, used under license to the IATF.

---

*Part of the Doesn't Mean Anything Cool GitHub of DOOM!!!* 💀
