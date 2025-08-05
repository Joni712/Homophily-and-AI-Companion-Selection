from os import environ

SESSION_CONFIGS = [
    dict(
        name="pilot",
        display_name="pilot session",
        app_sequence=["pilot"],
        num_demo_participants=1,
    ),
    dict(
        name="main",
        display_name="full session",
        app_sequence=["main"],
        num_demo_participants=1,
    ),
    dict(
        name="main_w_avatars",
        display_name="full session with avatar",
        app_sequence=["main"],
        num_demo_participants=1,
        participant_avatar=True
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=2.5,
    win_fee=1.0,
    tie_fee=0.5,
)

PARTICIPANT_FIELDS = ["seed", "task_sequence", "mode", "prolific_id", "avatar"]
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = False

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = "7452308657440"
