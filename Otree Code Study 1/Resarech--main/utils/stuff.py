from otree.api import BasePlayer, cu


def calc_outcome(our_score, their_score) -> int:
    if our_score > their_score:
        return +1
    elif our_score < their_score:
        return -1
    else:
        return 0


def calc_payoff(player: BasePlayer, outcome: int) -> cu:
    if outcome == +1:
        return cu(player.session.config["win_fee"])
    elif outcome == 0:
        return cu(player.session.config["tie_fee"])
    else:
        return cu(0)
