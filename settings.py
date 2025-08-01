from os import environ

SESSION_CONFIGS = [
    dict(
        name='pilotsurveyALL',
        app_sequence=['presurvey', 'mock', 'Pay', 'noPay'],
        #app_sequence = ['presurvey', 'mock'],  ### --- TESTS FOR LASMI --- ###
        num_demo_participants=12, # 6 conditions x 2 participants per condition (1 Rep 1 Dem)
        display_name="Combined app",
        # no consent, failed training, faield attention check
        returnlink='https://app.prolific.com/submissions/complete?cc=C68YG750', # no pay, no bonus
        # finished everything
        completelink='https://app.prolific.com/submissions/complete?cc=CTVV178T',
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['gives_consent', 'political_affiliation', 'scenario_type', 'training_attempt', 'training_success', 'no_consent', 'failed_commitment',
                      'treatment', 'scenario_order', 'all_responses', 'wait_page_arrival', 'failed_attention_check', 
                      'active', 'reason', 'scenario','anticonformist', 'no_nudge', 
                      'complete_presurvey','forced_response_counter',
                      'not_neutral', 'neighbors_configurations', 'neighbors',
                      'simulated_time', 'treatment_available']# For bots, this will be used to simulate wait time

SESSION_FIELDS = ['combined_responses', 
                  'AC_p', 'AC_n', 
                  'C_p', 'C_n', 
                  'NO_p', 'NO_n',
                  'AC_Dem_p', 'AC_Rep_p', 
                  'AC_Dem_n', 'AC_Rep_n',
                  'C_Dem_p', 'C_Rep_p', 
                  'C_Dem_n', 'C_Rep_n',
                  'NO_Dem_p', 'NO_Rep_p',
                  'NO_Dem_n', 'NO_Rep_n',]



ROOMS = [
    dict(
        name='pilot_20250724_1',
        display_name='pilot_20250724_1',
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
