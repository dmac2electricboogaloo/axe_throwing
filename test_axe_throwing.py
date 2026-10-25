"""Tests for axe_throwing.py. Run with:  python3 -m unittest -v"""

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import axe_throwing as at


def round_inputs(ann, bob, clutch=("N", "N")):
    """Typed answers for one round: ann and bob each have 5 scores.

    Throws 1-4 alternate Ann, Bob. Throw 5 first asks each player about
    Clutch, then takes both scores.
    """
    typed = []
    for i in range(4):
        typed += [str(ann[i]), str(bob[i])]
    typed += list(clutch)
    typed += [str(ann[4]), str(bob[4])]
    return typed


def run_main(typed, argv=()):
    """Run the whole program with scripted answers and return what it printed."""
    out = io.StringIO()
    with patch("builtins.input", side_effect=typed), redirect_stdout(out):
        at.main(list(argv))
    return out.getvalue()


class RuleTests(unittest.TestCase):
    def test_standard_throw_scores(self):
        self.assertEqual(at.allowed_scores(), (0, 1, 3, 5))

    def test_clutch_scores_seven_or_nothing(self):
        self.assertEqual(at.allowed_scores(clutch_called=True), (0, 7))

    def test_premier_touch_clutch_scores_five(self):
        self.assertEqual(at.allowed_scores(clutch_called=True, premier=True), (0, 5, 7))

    def test_parse_score_accepts_valid_scores(self):
        self.assertEqual(at.parse_score(" 3 ", at.STANDARD_SCORES), 3)
        self.assertEqual(at.parse_score("0", at.STANDARD_SCORES), 0)

    def test_parse_score_rejects_bad_input(self):
        for bad in ["", "six", "2", "4", "7", "-1", "3.5", "99"]:
            self.assertIsNone(at.parse_score(bad, at.STANDARD_SCORES), bad)

    def test_decide_winner(self):
        self.assertEqual(at.decide_winner([10, 8]), 0)
        self.assertEqual(at.decide_winner([8, 10]), 1)
        self.assertIsNone(at.decide_winner([9, 9]))

    def test_match_winner_by_rounds(self):
        self.assertEqual(at.match_winner([0, 0, 1]), 0)
        self.assertEqual(at.match_winner([1, 0, 1]), 1)
        self.assertEqual(at.match_winner([0, 0, 0]), 0)

    def test_match_winner_plurality_with_a_tied_round(self):
        # One round win and two ties still wins the match.
        self.assertEqual(at.match_winner([None, 1, None]), 1)

    def test_match_winner_is_none_when_rounds_are_tied(self):
        self.assertIsNone(at.match_winner([0, 1, None]))
        self.assertIsNone(at.match_winner([None, None, None]))


class MatchTests(unittest.TestCase):
    def test_two_rounds_wins_the_match_and_all_three_are_played(self):
        typed = ["ann", "bob"]
        typed += round_inputs([5, 5, 5, 5, 5], [1, 1, 1, 1, 1])  # Ann
        typed += round_inputs([3, 3, 3, 3, 3], [1, 1, 1, 1, 1])  # Ann
        typed += round_inputs([0, 0, 0, 0, 0], [5, 5, 5, 5, 5])  # Bob
        output = run_main(typed)
        self.assertIn("ROUND NUMBER 3, THROW NUMBER 5", output)
        self.assertIn("AND THE WINNER IS: ANN!!!", output)
        self.assertIn("ROUNDS WON:   ANN 2 - 1 BOB", output)
        self.assertIn("TOTAL POINTS: ANN 40 - 35 BOB", output)
        self.assertEqual(output.count("SWITCH LANES!"), 2)

    def test_a_player_can_win_the_match_with_one_round_and_two_ties(self):
        typed = ["ann", "bob"]
        typed += round_inputs([5, 5, 5, 5, 5], [3, 3, 3, 3, 3])  # Ann
        typed += round_inputs([3] * 5, [3] * 5)                  # tie
        typed += round_inputs([1] * 5, [1] * 5)                  # tie
        output = run_main(typed)
        self.assertIn("AND THE WINNER IS: ANN!!!", output)
        self.assertNotIn("BIG AXE", output)

    def test_tied_rounds_go_to_a_big_axe_sudden_death(self):
        typed = ["ann", "bob"]
        typed += round_inputs([5] * 5, [1] * 5)  # Ann
        typed += round_inputs([1] * 5, [5] * 5)  # Bob
        typed += round_inputs([3] * 5, [3] * 5)  # tie
        typed += ["2"]       # Bob throws first
        typed += ["3", "3"]  # tied, throw again
        typed += ["1", "5"]  # Bob scores 1, Ann scores 5 -> Ann wins
        output = run_main(typed)
        self.assertIn("BIG AXE TIEBREAKER", output)
        self.assertIn("STILL TIED", output)
        self.assertIn("AND THE WINNER, IN SUDDEN DEATH, IS: ANN!!!", output)

    def test_clutch_is_asked_about_only_on_the_final_throw(self):
        typed = ["ann", "bob"]
        typed += round_inputs([1] * 5, [1] * 5)
        typed += round_inputs([1] * 5, [1] * 5)
        typed += round_inputs([1] * 5, [1] * 5)
        typed += ["1", "1", "5"]  # tiebreaker: Ann throws first; Ann 1, Bob 5
        with patch("builtins.input", side_effect=typed) as fake_input, \
                redirect_stdout(io.StringIO()):
            at.main([])
        prompts = [call.args[0] for call in fake_input.call_args_list]
        clutch_prompts = [p for p in prompts if "CALL CLUTCH?" in p]
        self.assertEqual(len(clutch_prompts), 6)  # 3 rounds x 2 players

    def test_called_clutch_scores_seven(self):
        typed = ["ann", "bob"]
        typed += round_inputs([0, 0, 0, 0, 7], [3, 0, 0, 0, 3], clutch=("Y", "N"))
        typed += round_inputs([0] * 5, [0] * 5)
        typed += round_inputs([0] * 5, [0] * 5)
        output = run_main(typed)
        self.assertIn("ROUND 1: ANN 7 - 6 BOB  (ANN WINS)", output)

    def test_seven_is_rejected_without_a_clutch_call(self):
        typed = ["ann", "bob"]
        typed += ["1", "0"] * 4 + ["N", "N"] + ["7", "5", "5"]  # 7 refused, retry
        typed += round_inputs([0] * 5, [0] * 5)
        typed += round_inputs([0] * 5, [0] * 5)
        output = run_main(typed)
        self.assertIn("THAT IS NOT A VALID SCORE", output)
        self.assertIn("ROUND 1: ANN 9 - 5 BOB", output)

    def test_bad_names_and_scores_are_asked_again(self):
        typed = ["", "ann", "ann", "bob"]  # empty name, then duplicate name
        typed += ["six", "", "-1", "1", "1"] + ["1", "1"] * 3 + ["N", "N", "1", "1"]
        typed += round_inputs([1] * 5, [1] * 5)
        typed += round_inputs([1] * 5, [1] * 5)
        typed += ["1", "1", "3"]  # tiebreaker: Ann throws first; Ann 1, Bob 3
        output = run_main(typed)
        self.assertIn("NEEDS A NAME", output)
        self.assertIn("DIFFERENT NAMES", output)
        self.assertEqual(output.count("THAT IS NOT A VALID SCORE"), 3)

    def test_premier_flag_allows_touch_clutch(self):
        typed = ["ann", "bob"]
        typed += round_inputs([0, 0, 0, 0, 5], [0] * 5, clutch=("Y", "N"))
        typed += round_inputs([0] * 5, [0] * 5)
        typed += round_inputs([0] * 5, [0] * 5)
        output = run_main(typed, argv=["--premier"])
        self.assertIn("ROUND 1: ANN 5 - 0 BOB  (ANN WINS)", output)

    def test_touch_clutch_value_is_rejected_on_standard_rules(self):
        typed = ["ann", "bob"]
        typed += ["0", "0"] * 4 + ["Y", "N"] + ["5", "7", "0"]  # 5 refused, then 7
        typed += round_inputs([0] * 5, [0] * 5)
        typed += round_inputs([0] * 5, [0] * 5)
        output = run_main(typed)
        self.assertIn("CHOOSE FROM: 0, 7", output)
        self.assertIn("ROUND 1: ANN 7 - 0 BOB  (ANN WINS)", output)


if __name__ == "__main__":
    unittest.main()
