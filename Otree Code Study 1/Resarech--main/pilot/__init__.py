import random
from dataclasses import asdict
from pathlib import Path

from otree.api import *

from utils import bots_utils, csv_utils, tasks_utils
from utils.stuff import calc_outcome, calc_payoff

DATADIR = Path(__file__).parent.parent / "data"
BOTSDATA = bots_utils.read_bots(DATADIR / "bots.csv")
NAMESDATA = bots_utils.read_names(DATADIR / "names.csv")
TASKDATA = tasks_utils.read(DATADIR / "tasks.csv")
RESULTS = csv_utils.read_csv(DATADIR / "simulated.csv", {"score": int})


def sample_score():
    return random.choice(RESULTS)["score"]


class C(BaseConstants):
    NAME_IN_URL = "pilot"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    prolific_id = models.StringField()

    competitor = models.StringField()
    answers = models.StringField()
    expected = models.StringField()
    score = models.IntegerField()

    competitor_score = models.IntegerField()
    outcome = models.IntegerField()

    attention = models.BooleanField()


def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        if "seed" not in p.participant.vars:
            p.participant.mode = "bots"
            p.participant.seed = hash(p.participant)
            p.participant.prolific_id = None


def calc_results(player: Player):
    """Calc result for part 1 with competitor"""
    player.score = tasks_utils.score(player.answers, player.expected)
    player.competitor_score = sample_score()
    player.outcome = calc_outcome(player.score, player.competitor_score)
    player.payoff = calc_payoff(player, player.outcome)


# PAGES


class Consent(Page):
    template_name = "Consent.html"


class ProlificID(Page):
    template_name = "ProlificID.html"
    form_model = "player"
    form_fields = ["prolific_id"]

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.prolific_id = player.prolific_id


class GeneralInstructions(Page):
    template_name = "GeneralInstructions.html"


class Practice(Page):
    template_name = "Practice.html"
    timeout_seconds = 60

    @staticmethod
    def vars_for_template(player: Player):
        tasks = tasks_utils.select(TASKDATA, section="practice")
        return dict(task=asdict(tasks[0]))


class PracticeEnd(Page):
    template_name = "PracticeEnd.html"


class Instructions1(Page):
    template_name = "Instructions1.html"


class Choice(Page):
    template_name = "Choice1.html"
    form_model = "player"
    form_fields = ["competitor"]

    @staticmethod
    def vars_for_template(player: Player):
        bots = bots_utils.merge_names(BOTSDATA, NAMESDATA, seed=player.participant.seed)
        bots = bots_utils.select(bots, section="part 1", seed=player.participant.seed)
        return dict(bots=bots, bot_field="competitor")


class Start(Page):
    template_name = "Start.html"


class Match(Page):
    template_name = "Match.html"
    form_model = "player"
    form_fields = ["answers"]
    timeout_seconds = 150

    @staticmethod
    def vars_for_template(player: Player):
        competitor = bots_utils.parse(player.competitor)
        return dict(competitor=competitor, teammate=None)

    @staticmethod
    def js_vars(player: Player):
        tasks = tasks_utils.select(TASKDATA, section="part 1", seed=player.participant.seed)
        player.expected = tasks_utils.answers(tasks)
        return dict(tasks=[asdict(t) for t in tasks])

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        calc_results(player)


class Results(Page):
    template_name = "ResultsP.html"

    @staticmethod
    def vars_for_template(player: Player):
        return dict(outcome=player.outcome)


class AttentionCheck(Page):
    template_name = "AttentionCheck.html"
    form_model = "player"
    form_fields = ["attention"]


class Debrief(Page):
    template_name = "Debrief.html"


page_sequence = [
    Consent,
    ProlificID,
    GeneralInstructions,
    Practice,
    PracticeEnd,
    Instructions1,
    Choice,
    Start,
    Match,
    Results,
    AttentionCheck,
    Debrief,
]


def custom_export(players):
    yield [
        "participant.code",
        "participant.label",
        "participant.mode",
        "participant.prolific_id",
        "attention",
        #
        "competitor",
        "competitor_race",
        "competitor_gender",
        "competitor_score",
        "score",
        "outcome",
    ]

    def out(val):
        "formats outcome as -1/0/+1"
        if val is None:
            return None
        return f"{val:+1}"

    for player in players:
        competitor = bots_utils.parse(player.competitor)
        yield [
            player.participant.code,
            player.participant.label,
            player.participant.mode,
            player.participant.prolific_id,
            player.attention,
            #
            competitor,
            competitor.race,
            competitor.gender,
            player.competitor_score,
            player.score,
            out(player.outcome),
        ]
