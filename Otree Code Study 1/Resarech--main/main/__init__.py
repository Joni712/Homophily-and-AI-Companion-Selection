import random
from dataclasses import asdict
from pathlib import Path
import itertools

from otree.api import *
from otree.models.participant import Participant

from utils import bots_utils, csv_utils, tasks_utils
from utils.pageseq_utils import task_page
from utils.stuff import calc_outcome, calc_payoff

DATADIR = Path(__file__).parent.parent / "data"
BOTSDATA = bots_utils.read_bots(DATADIR / "bots.csv")
NAMESDATA = bots_utils.read_names(DATADIR / "names.csv")
TASKDATA = tasks_utils.read(DATADIR / "tasks.csv")

SIMULATION = csv_utils.read_csv(DATADIR / "simulated.csv", {"score": int})
RESULTS = csv_utils.read_csv(DATADIR / "results.csv", {"gender": str, "score": int})


class C(BaseConstants):
    NAME_IN_URL = "main"
    PLAYERS_PER_GROUP = None
    TASKS = ["p1", "p2", "p3"]
    NUM_ROUNDS = 5  # start + 3 tasks + final

    MODES = ("bots", "humans")


def sample_score(bot: bots_utils.Bot, mode: str):
    if mode == "humans":
        results = csv_utils.filter_data(RESULTS, gender=bot.gender)
        return random.choice(results)["score"]
    else:
        return random.choice(SIMULATION)["score"]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    prolific_id = models.StringField()
    avatar = models.StringField()
    
    current_task = models.StringField()
    answers = models.StringField()
    expected = models.StringField()
    score = models.IntegerField()

    p1_competitor = models.StringField()
    p1_competitor_score = models.IntegerField()
    p1_score = models.IntegerField()
    p1_outcome = models.IntegerField()

    p2_teammate = models.StringField()
    p2_teammate_score = models.IntegerField()
    p2_competitor = models.StringField()
    p2_competitor_score = models.IntegerField()
    p2_score = models.IntegerField()
    p2_outcome = models.IntegerField()

    p3_teammate = models.StringField()
    p3_competitor = models.StringField()
    p3_decision = models.StringField(choices=("compete", "pass"))
    p3_teammate_score1 = models.IntegerField()
    p3_teammate_score2 = models.IntegerField()
    p3_competitor_score = models.IntegerField()
    p3_score = models.IntegerField()
    p3_outcome = models.IntegerField()

    attention = models.BooleanField()


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        # initialize tasks sequence
        for p in subsession.get_players():
            p.participant.seed = hash(p.participant)
            p.participant.mode = random.choice(C.MODES)
            seq = list(C.TASKS)
            random.shuffle(seq)
            p.participant.task_sequence = ["start"] + seq + ["end"]
            p.participant.prolific_id = None
            p.participant.avatar = None

    bots2 = bots_utils.select(BOTSDATA, section="part 2")
    bots3 = bots_utils.select(BOTSDATA, section="part 3")
    teammate3 = list(filter(lambda b: b.id == 25, bots3))[0]
    competitors3 = list(filter(lambda b: b.id in (26, 27), bots3))

    # pick up current task for each player
    for player in subsession.get_players():
        player.current_task = player.participant.task_sequence[subsession.round_number - 1]

        if player.current_task == "p2":
            player.p2_competitor = str(random.choice(bots2))

        if player.current_task == "p3":
            player.p3_teammate = str(teammate3)
            player.p3_competitor = str(random.choice(competitors3))


def team_score(score1, score2):
    return round((score1 + score2) / 2)


def calc_results0(player: Player):
    """Player own score"""
    player.score = tasks_utils.score(player.answers, player.expected)


def calc_results1(player: Player):
    """ "Calc result for part 1 with competitor"""
    calc_results0(player)
    p1_competitor = bots_utils.parse(player.p1_competitor)
    player.p1_competitor_score = sample_score(p1_competitor, player.participant.mode)
    player.p1_score = player.score
    player.p1_outcome = calc_outcome(player.p1_score, player.p1_competitor_score)
    player.payoff = calc_payoff(player, player.p1_outcome)


def calc_results2(player: Player):
    """ "Calc result for part 2 with teammate and competitor"""
    calc_results0(player)
    p2_competitor = bots_utils.parse(player.p2_competitor)
    p2_teammate = bots_utils.parse(player.p2_teammate)
    player.p2_competitor_score = sample_score(p2_competitor, player.participant.mode)
    player.p2_teammate_score = sample_score(p2_teammate, player.participant.mode)
    player.p2_score = team_score(player.score, player.p2_teammate_score)
    player.p2_outcome = calc_outcome(player.p2_score, player.p2_competitor_score)
    player.payoff = calc_payoff(player, player.p2_outcome)


def calc_results3_competed(player: Player):
    """Calc results for part 3 with player competed"""
    calc_results0(player)
    p3_competitor = bots_utils.parse(player.p3_competitor)
    p3_teammate = bots_utils.parse(player.p3_teammate)
    player.p3_competitor_score = sample_score(p3_competitor, player.participant.mode)
    player.p3_teammate_score1 = sample_score(p3_teammate, player.participant.mode)
    player.p3_score = team_score(player.score, player.p3_teammate_score1)
    player.p3_outcome = calc_outcome(player.p3_score, player.p3_competitor_score)
    player.payoff = calc_payoff(player, player.p3_outcome)


def calc_results3_skipped(player: Player):
    """Calc results for part 3 with player passed"""
    p3_competitor = bots_utils.parse(player.p3_competitor)
    p3_teammate = bots_utils.parse(player.p3_teammate)
    player.p3_competitor_score = sample_score(player.participant.mode, ...)
    player.p3_teammate_score1 = sample_score(player.participant.mode, ...)
    player.p3_teammate_score2 = sample_score(player.participant.mode, ...)
    player.p3_score = team_score(player.p3_teammate_score1, player.p3_teammate_score2)
    player.p3_outcome = calc_outcome(player.p3_score, player.p3_competitor_score)
    player.payoff = calc_payoff(player, player.p3_outcome)


# PAGES


@task_page("start")
class Consent(Page):
    template_name = "Consent.html"


@task_page("start")
class ProlificID(Page):
    template_name = "ProlificID.html"
    form_model = "player"
    form_fields = ["prolific_id"]

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.prolific_id = player.prolific_id


@task_page("start")
class GeneralInstructions(Page):
    template_name = "GeneralInstructions.html"


@task_page("start")
class Practice(Page):
    template_name = "Practice.html"
    timeout_seconds = 60

    @staticmethod
    def vars_for_template(player: Player):
        tasks = tasks_utils.select(TASKDATA, section="practice")
        return dict(task=asdict(tasks[0]))


@task_page("start")
class PracticeEnd(Page):
    template_name = "PracticeEnd.html"


@task_page("start")
class AvatarChoice(Page):
    template_name = "AvatarChoice.html"
    form_model = "player"
    form_fields = ["avatar"]

    @staticmethod
    def is_displayed(player: Player):
        return player.session.config.get("participant_avatar")

    @staticmethod
    def vars_for_template(player: Player):
        avatars = bots_utils.select(BOTSDATA, section="avatar")
        return dict(bots=avatars, bot_field="avatar")

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.avatar = player.avatar


#### PART 1


@task_page("p1")
class Instructions1(Page):
    template_name = "Instructions1.html"


@task_page("p1")
class Choice1(Page):
    template_name = "Choice1.html"
    form_model = "player"
    form_fields = ["p1_competitor"]

    @staticmethod
    def vars_for_template(player: Player):
        bots = bots_utils.merge_names(BOTSDATA, NAMESDATA, seed=player.participant.seed)
        bots = bots_utils.select(bots, section="part 1", seed=player.participant.seed)
        return dict(bots=bots, bot_field="p1_competitor")


@task_page("p1")
class Start1(Page):
    template_name = "Start.html"


@task_page("p1")
class Match1(Page):
    template_name = "Match.html"
    form_model = "player"
    form_fields = ["answers"]
    timeout_seconds = 150

    @staticmethod
    def vars_for_template(player: Player):
        competitor = bots_utils.parse(player.p1_competitor)
        return dict(competitor=competitor, teammate=None)

    @staticmethod
    def js_vars(player: Player):
        tasks = tasks_utils.select(TASKDATA, section="part 1", seed=player.participant.seed)
        player.expected = tasks_utils.answers(tasks)
        return dict(tasks=[asdict(t) for t in tasks])

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        calc_results1(player)


@task_page("p1")
class Results1(Page):
    template_name = "Results1.html"

    @staticmethod
    def vars_for_template(player: Player):
        return dict(outcome=player.p1_outcome)


#### PART 2


@task_page("p2")
class Instructions2(Page):
    template_name = "Instructions2.html"


@task_page("p2")
class Choice2(Page):
    template_name = "Choice2.html"
    form_model = "player"
    form_fields = ["p2_teammate"]

    @staticmethod
    def vars_for_template(player: Player):
        bots = bots_utils.merge_names(BOTSDATA, NAMESDATA, seed=player.participant.seed)
        bots = bots_utils.select(bots, section="part 2", seed=player.participant.seed)
        return dict(bots=bots, bot_field="p2_teammate")


@task_page("p2")
class Start2(Page):
    template_name = "Start.html"


@task_page("p2")
class Match2(Page):
    template_name = "Match.html"
    form_model = "player"
    form_fields = ["answers"]
    timeout_seconds = 150

    @staticmethod
    def vars_for_template(player: Player):
        teammate = bots_utils.parse(player.p2_teammate)
        return dict(competitor=None, teammate=teammate)

    @staticmethod
    def js_vars(player: Player):
        tasks = tasks_utils.select(TASKDATA, section="part 2", seed=player.participant.seed)
        player.expected = tasks_utils.answers(tasks)
        return dict(tasks=[asdict(t) for t in tasks])

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        calc_results2(player)


@task_page("p2")
class Results2(Page):
    template_name = "Results2.html"

    @staticmethod
    def vars_for_template(player: Player):
        return dict(outcome=player.p2_outcome)


#### PART 3


@task_page("p3")
class Instructions3(Page):
    template_name = "Instructions3.html"


@task_page("p3")
class Choice3(Page):
    template_name = "Choice3.html"
    form_model = "player"
    form_fields = ["p3_decision"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            competitor=bots_utils.parse(player.p3_competitor),
            teammate=bots_utils.parse(player.p3_teammate),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.p3_decision == "pass":
            calc_results3_skipped(player)


@task_page("p3")
class Start3(Page):
    template_name = "Start.html"

    @staticmethod
    def is_displayed(player: Player):
        return player.p3_decision == "compete"


@task_page("p3")
class Match3(Page):
    template_name = "Match.html"
    form_model = "player"
    form_fields = ["answers"]
    timeout_seconds = 150

    @staticmethod
    def is_displayed(player: Player):
        return player.p3_decision == "compete"

    @staticmethod
    def vars_for_template(player: Player):
        teammate = bots_utils.parse(player.p3_teammate)
        competitor = bots_utils.parse(player.p3_competitor)
        return dict(competitor=competitor, teammate=teammate)

    @staticmethod
    def js_vars(player: Player):
        tasks = tasks_utils.select(TASKDATA, section="part 3", seed=player.participant.seed)
        player.expected = tasks_utils.answers(tasks)
        return dict(tasks=[asdict(t) for t in tasks])

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        calc_results3_competed(player)


@task_page("p3")
class Results3(Page):
    template_name = "Results3.html"

    @staticmethod
    def vars_for_template(player: Player):
        teammate = bots_utils.parse(player.p3_teammate)
        competitor = bots_utils.parse(player.p3_competitor)
        return dict(competitor=competitor, teammate=teammate, outcome=player.p3_outcome)


### END


@task_page("end")
class AttentionCheck(Page):
    template_name = "AttentionCheck.html"
    form_model = "player"
    form_fields = ["attention"]


@task_page("end")
class Debrief(Page):
    template_name = "Debrief.html"


page_sequence = [
    # start
    Consent,
    ProlificID,
    GeneralInstructions,
    Practice,
    PracticeEnd,
    AvatarChoice,
    # p1
    Instructions1,
    Choice1,
    Start1,
    Match1,
    Results1,
    # p2
    Instructions2,
    Choice2,
    Start2,
    Match2,
    Results2,
    # p3
    Instructions3,
    Choice3,
    Start3,
    Match3,
    Results3,
    # end
    AttentionCheck,
    Debrief,
]


def custom_export(players):
    yield [
        "participant.code",
        "participant.label",
        "participant.mode",
        "participant.prolific_id",
        "sequence",
        "participant.avatar",
        "participant.avatar_race",
        "participant.avatar_gender",
        "attention",
        #
        "p1_competitor",
        "p1_competitor_race",
        "p1_competitor_gender",
        "p1_competitor_score",
        "p1_score",
        "p1_outcome",
        #
        "p2_teammate",
        "p2_teammate_race",
        "p2_teammate_gender",
        "p2_competitor",
        "p2_competitor_race",
        "p2_competitor_gender",
        "p2_teammate_score",
        "p2_competitor_score",
        "p2_score",
        "p2_outcome",
        #
        "p3_teammate",
        "p3_teammate_race",
        "p3_teammate_gender",
        "p3_competitor",
        "p3_competitor_race",
        "p3_competitor_gender",
        "p3_decision",
        "p3_teammate_score1",
        "p3_teammate_score2",
        "p3_competitor_score",
        "p3_score",
        "p3_outcome",
    ]

    def out(val):
        "formats outcome as -1/0/+1"
        if val is None:
            return None
        return f"{val:+1}"

    # regroup players by participants
    players.sort(key=lambda p: p.participant_id)
    grouped = itertools.groupby(players, key=lambda p: p.participant)

    for participant, p_players in grouped:
        allplayers = list(p_players)
        seq = ",".join(filter(lambda t: t in C.TASKS, participant.task_sequence))

        rowdata = [participant.code, participant.label, participant.mode, participant.prolific_id, seq]

        if participant.session.config.get('participant_avatar'):
            avatar = bots_utils.parse(participant.avatar)
            rowdata += [
                avatar,
                avatar.race,
                avatar.gender
            ]
        else:
            rowdata += [None, None, None]

        try:
            [player] = filter(lambda p: p.current_task == "end", allplayers)
        except ValueError:
            rowdata += [None]
        else:
            rowdata += [player.attention]

        try:
            [player] = filter(lambda p: p.current_task == "p1", allplayers)
        except ValueError:
            rowdata += [None, None, None, None, None, None]
        else:
            competitor = bots_utils.parse(player.p1_competitor)
            rowdata += [
                player.p1_competitor,
                competitor.race,
                competitor.gender,
                player.p1_competitor_score,
                player.p1_score,
                out(player.p1_outcome),
            ]

        try:
            [player] = filter(lambda p: p.current_task == "p2", allplayers)
        except ValueError:
            rowdata += [None, None, None, None, None, None, None, None, None, None]
        else:
            teammate = bots_utils.parse(player.p2_teammate)
            competitor = bots_utils.parse(player.p2_competitor)
            rowdata += [
                player.p2_teammate,
                teammate.race,
                teammate.gender,
                player.p2_competitor,
                competitor.race,
                competitor.gender,
                player.p2_teammate_score,
                player.p2_competitor_score,
                player.p2_score,
                out(player.p2_outcome),
            ]

        try:
            [player] = filter(lambda p: p.current_task == "p3", allplayers)
        except ValueError:
            rowdata += [None, None, None, None, None, None, None, None, None, None]
        else:
            teammate = bots_utils.parse(player.p3_teammate)
            competitor = bots_utils.parse(player.p3_competitor)
            rowdata += [
                player.p3_teammate,
                teammate.race,
                teammate.gender,
                player.p3_competitor,
                competitor.race,
                competitor.gender,
                player.p3_decision,
                player.p3_teammate_score1,
                player.p3_teammate_score2,
                player.p3_competitor_score,
                player.p3_score,
                out(player.p3_outcome),
            ]

        yield rowdata
