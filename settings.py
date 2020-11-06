from os import environ

app_sequence = ['quiz', 'last']
SESSION_CONFIGS = [
    dict(
        name='baseline',
        display_name="Baseline",
        num_demo_participants=1,
        app_sequence=app_sequence,
        tp=False,
        stress=False
    ),
    dict(
        name='tp',
        display_name="TP Treatment",
        num_demo_participants=1,
        app_sequence=app_sequence,
        tp=True,
        stress=False
    ),
    dict(
        name='stress',
        display_name="TP+Stress treatment",
        num_demo_participants=1,
        app_sequence=app_sequence,
        tp=True,
        stress=True
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'ru'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False

ROOMS = []

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
REAL_WORLD_CURRENCY_DECIMAL_PLACES = 2
DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = 'w^ww##qzlm)kv=zz*y_re8)f-drx3f12e=35mkncqi@xcrxf0d'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']
