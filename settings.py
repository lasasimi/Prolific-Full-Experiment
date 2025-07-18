from os import environ

SESSION_CONFIGS = [
    dict(
        name='pilotsurveyALL',
        app_sequence=['presurvey', 'mock', 'Pay', 'noPay'],
        #app_sequence = ['presurvey', 'mock'],  ### --- TESTS FOR LASMI --- ###
        num_demo_participants=8, # 9x4 + 9x8
        display_name="Combined app",
        # no consent, failed training, faield attention check, and became inactive in mock app
        returnlink='https://app.prolific.com/submissions/complete?cc=C68YG750', # no pay, no bonus
        # finished presurvey, no commitment
        basepaylink='https://app.prolific.com/submissions/complete?cc=COQQW3A7', # base pay only
        # finished presurvey, commitment, waited too long OR completed mock app
        bonuslink=' https://app.prolific.com/submissions/complete?cc=CTVV178T', # base pay + waiting bonus OR max pay
        scenario_id='s3_n',
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['gives_consent', 'training_attempt', 'training_success', 'no_consent', 'failed_commitment',
                      'treatment', 'scenario_order', 'all_responses', 'wait_page_arrival', 'failed_attention_check', 
                      'active', 'single_group', 'reason','player_ids', 'group_size', 'is_group_single',
                      'scenario','anticonformist','position','own_faction','other_faction','discussion_grp','complete_presurvey',
                      'eligible_notneutral',
                      'simulated_time']# For bots, this will be used to simulate wait time
SESSION_FIELDS = ['combined_responses','AC_n', 'C_n', 'AC_p', 'C_p']



ROOMS = [
    dict(
        name='pilotsession1_20250625',
        display_name='pilotsession1_20250625',
    ),
]


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
