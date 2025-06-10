from os import environ

SESSION_CONFIGS = [
    dict(
        name='pilotsurveyALL',
        app_sequence=['presurvey', 'mock'],
        num_demo_participants=3,
        display_name="Combined app",
        completionlink=' https://app.prolific.com/submissions/complete?cc=CA6AFDZ5',
        didnotconsent='https://app.prolific.com/submissions/complete?cc=C1KPU2A9',
    ),

]



# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['gives_consent', 'no_consent', 'treatment', 'scenario_order', 'all_responses', 'wait_page_arrival']
SESSION_FIELDS = ['combined_responses']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '5749958540088'
