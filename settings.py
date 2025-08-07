from os import environ

SESSION_CONFIGS = [
    dict(
        name='pilotsurveyALL',
        app_sequence=['presurvey', 'mock', 'noPay', 'Pay'],
        #app_sequence = ['presurvey', 'mock'],  ### --- TESTS FOR LASMI --- ###
        num_demo_participants=20, # N08 N04 (must be a multiple of 4)
        display_name="Combined app",
        # no consent, failed training, faield attention check, and became inactive in mock app
        returnlink='https://app.prolific.com/submissions/complete?cc=CUN28996', # no pay, no bonus
        # finished presurvey, no commitment
        basepaylink='https://app.prolific.com/submissions/complete?cc=CMKI4JO9', # base pay only
        # finished presurvey, commitment, waited too long OR completed mock app
        bonuslink=' https://app.prolific.com/submissions/complete?cc=C1AKEBMQ', # base pay + waiting bonus OR max pay
        # maximum groups in each condition
        N04_p00 = 0,
        N04_p25 = 1,
        N04_p50 = 1,
        N08_p00 = 0,
        N08_p25 = 1,
        N08_p50 = 1,
    )
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
                      'eligible_notneutral', 'forced_response_counter',
                      'simulated_time']# For bots, this will be used to simulate wait time
SESSION_FIELDS = ['combined_responses','scenario_counts', 'N04_p00','N04_p25','N04_p50','N08_p00' ,'N08_p25','N08_p50',
                  'MAX_N04_p00','MAX_N04_p25','MAX_N04_p50','MAX_N08_p00','MAX_N08_p25','MAX_N08_p50']



ROOMS = [
    dict(
        name='fullexperiment_20250807',
        display_name='fullexperiment_20250807',
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
