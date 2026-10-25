"""THE HOUSE OF AXE THROWING: a two-player match scorekeeper.

Scoring follows the IATF standard league format:
  * A match is 3 rounds of 5 throws per player, and every round is thrown.
  * The higher point total wins each round; win 2 of 3 rounds to win the match.
  * Players tied on rounds settle it with a sudden-death Big Axe tiebreaker.
  * Throws score 0 (miss or drop), 1, 3 or 5. On the 5th throw of a round a
    player may call Clutch, which scores 7 (or 0 if it is missed).

Run it with:  python3 axe_throwing.py            (standard rules)
              python3 axe_throwing.py --premier  (touch Clutch is worth 5)
"""

import argparse
from random import choice

ROUNDS_PER_MATCH = 3
THROWS_PER_ROUND = 5

STANDARD_SCORES = (0, 1, 3, 5)  # 0 means a miss or a drop
CLUTCH_SCORE = 7
TOUCH_CLUTCH_SCORE = 5  # Premier rules only

INTRO_CHOICES = [
    "LET US PREPARE TO WATCH THESE TWO TITANS BATTLE IT OUT: ",
    "TONIGHT IS ANOTHER CHAPTER IN THE IMMORTAL BATTLE BETWEEN: ",
    "GATHER AROUND BECAUSE IT WILL BE A BLOOD BATH WHEN IT IS: ",
    "MARVEL AT THE AWESOMENESS WHEN YOU SEE THESE TWO FIGHT TO THE DEATH!!!: ",
    "GATHER AROUND AND BE A WITNESS TO THE UNDOING OF ALL YOU KNOW, WHEN IT IS: ",
]


# ---------------------------------------------------------------------------
# Rules (no input or output here, so they are easy to test)
# ---------------------------------------------------------------------------

def allowed_scores(clutch_called=False, premier=False):
    """Return the scores a single throw may be worth.

    Once Clutch is called, only the Clutch area counts, so every other
    area scores zero.
    """
    if not clutch_called:
        return STANDARD_SCORES
    if premier:
        return (0, TOUCH_CLUTCH_SCORE, CLUTCH_SCORE)
    return (0, CLUTCH_SCORE)


def parse_score(text, allowed):
    """Turn typed text into a score, or return None if it is not allowed."""
    text = text.strip()
    if text.isdecimal() and int(text) in allowed:
        return int(text)
    return None


def decide_winner(values):
    """Return 0 or 1 for the player with the higher value, or None for a tie."""
    if values[0] > values[1]:
        return 0
    if values[1] > values[0]:
        return 1
    return None


def match_winner(round_winners):
    """Return the player who won more rounds, or None if rounds are tied.

    round_winners holds 0, 1 or None (a tied round) for each round played.
    """
    rounds_won = [round_winners.count(0), round_winners.count(1)]
    return decide_winner(rounds_won)


# ---------------------------------------------------------------------------
# Asking questions (each one repeats until it gets a usable answer)
# ---------------------------------------------------------------------------

def ask_name(prompt, taken=None):
    while True:
        name = input(prompt).strip().upper()
        if not name:
            print("EVEN AN AXE THROWER NEEDS A NAME. TRY AGAIN!")
        elif name == taken:
            print("THE TWO PLAYERS NEED DIFFERENT NAMES. TRY AGAIN!")
        else:
            return name


def ask_yes_no(question):
    while True:
        answer = input(f"{question} (Y/N): ").strip().upper()
        if answer in ("Y", "N"):
            return answer == "Y"
        print("PLEASE ANSWER Y OR N.")


def ask_score(player, allowed):
    options = ", ".join(str(score) for score in allowed)
    while True:
        score = parse_score(input(f"{player} SCORES A ({options}): "), allowed)
        if score is not None:
            return score
        print(f"THAT IS NOT A VALID SCORE. CHOOSE FROM: {options}")


def ask_first_thrower(players):
    print("ROCK, PAPER, SCISSORS! THE WINNER CHOOSES WHO THROWS FIRST.")
    while True:
        answer = input(f"WHO THROWS FIRST? 1 = {players[0]}, 2 = {players[1]}: ").strip()
        if answer in ("1", "2"):
            return int(answer) - 1
        print("PLEASE ENTER 1 OR 2.")


# ---------------------------------------------------------------------------
# Playing the match
# ---------------------------------------------------------------------------

def print_score_line(players, totals):
    for player, total in zip(players, totals):
        print(f"The score is {player.upper()} {total}")


def play_round(players, round_number, premier=False):
    """Play one round of throws and return each player's total for it."""
    totals = [0, 0]
    for throw in range(1, THROWS_PER_ROUND + 1):
        print(f"ROUND NUMBER {round_number}, THROW NUMBER {throw}")
        clutch_calls = [False, False]
        if throw == THROWS_PER_ROUND:
            print("FINAL AXE OF THE ROUND! PLAYERS, CONFER ON YOUR CALLS.")
            clutch_calls = [ask_yes_no(f"DOES {player} CALL CLUTCH?") for player in players]
        for i, player in enumerate(players):
            totals[i] += ask_score(player, allowed_scores(clutch_calls[i], premier))
        print_score_line(players, totals)
    return totals


def play_big_axe(players):
    """Sudden death: one throw each until the scores differ. Returns the winner."""
    print("THE ROUNDS ARE TIED! IT IS TIME FOR THE BIG AXE TIEBREAKER!!!")
    first = ask_first_thrower(players)
    order = [first, 1 - first]
    while True:
        scores = [0, 0]
        for i in order:
            scores[i] = ask_score(players[i], STANDARD_SCORES)
        winner = decide_winner(scores)
        if winner is not None:
            return winner
        print("STILL TIED! GRAB THE BIG AXES AND THROW AGAIN!")


def print_scoreboard(players, round_totals, round_winners):
    print()
    print("FINAL SCOREBOARD")
    for number, (totals, winner) in enumerate(zip(round_totals, round_winners), start=1):
        result = "TIE" if winner is None else f"{players[winner]} WINS"
        print(f"ROUND {number}: {players[0]} {totals[0]} - {totals[1]} {players[1]}  ({result})")
    total_points = [sum(totals[i] for totals in round_totals) for i in range(2)]
    rounds_won = [round_winners.count(0), round_winners.count(1)]
    print(f"ROUNDS WON:   {players[0]} {rounds_won[0]} - {rounds_won[1]} {players[1]}")
    print(f"TOTAL POINTS: {players[0]} {total_points[0]} - {total_points[1]} {players[1]}")


def play_match(players, premier=False):
    """Play a full match and return the index of the winning player."""
    round_totals = []
    round_winners = []
    for round_number in range(1, ROUNDS_PER_MATCH + 1):
        if round_number > 1:
            print("SWITCH LANES!")
        totals = play_round(players, round_number, premier)
        winner = decide_winner(totals)
        round_totals.append(totals)
        round_winners.append(winner)
        if winner is None:
            print("ROUND ENDS IN A TIE!!!")
        else:
            print(f"{players[winner]} TAKES THE ROUND!!!")

    print_scoreboard(players, round_totals, round_winners)

    winner = match_winner(round_winners)
    if winner is None:
        winner = play_big_axe(players)
        print(f"AND THE WINNER, IN SUDDEN DEATH, IS: {players[winner]}!!!")
    else:
        print(f"AND THE WINNER IS: {players[winner]}!!!")
    return winner


def main(argv=None):
    parser = argparse.ArgumentParser(description="Score an axe throwing match.")
    parser.add_argument("--premier", action="store_true",
                        help="use Premier rules, where a touch Clutch is worth 5")
    args = parser.parse_args(argv)

    print("WELCOME TO THE HOUSE OF AXE THROWING!!!!")
    player_one = ask_name("PLEASE ENTER THE NAME OF THE FIRST PLAYER: ")
    player_two = ask_name("PLEASE ENTER THE NAME OF THE SECOND PLAYER: ", taken=player_one)
    print(choice(INTRO_CHOICES))
    print(f"{player_one} VERSUS {player_two}!!!!")
    play_match([player_one, player_two], premier=args.premier)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nMATCH CALLED OFF. THE AXES ARE RESTING.")
