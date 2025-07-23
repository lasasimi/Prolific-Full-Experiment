from otree.api import *
import pandas as pd # type: ignore
import numpy as np # type: ignore
import random 
import time

doc = """
Pre-survey for the Prolific Full Experiment.
This app collects demographic information and responses to a series of scenarios (only +1 For or -1 Against)
We will add a task training, and an attention check.
After pre-survey, participants will be redirected to the main experiment app (and we send the data from this app for the Grouping)
Whilst we group them, they will see a waiting page, ideally with a description of the task or a game to play.
"""

def open_CSV(filename):
    """
    :param filename: opinions.csv
    :return: a list of statements for the session
    """
    temp = pd.read_csv(filename, sep=',')
    return temp


class C(BaseConstants):
    NAME_IN_URL = 'presurvey'
    PLAYERS_PER_GROUP = None
    CSV = open_CSV('presurvey/3scenarios_pilot_np.csv')
    SCENARIOS = CSV.to_dict(orient='records')
    NUM_ROUNDS = 3 # number of scenarios -> change depending the number of scenarios you want to test

    # CHANGE N BEFORE LAUNCHING THE EXPERIMENT
    # N = total recruited / 6
    RECRUITED = 12 # total number of participants recruited in prolific, minimum 12 (1 Rep + 1 Dem)
    N = RECRUITED / 6 # number of participants per treatment (e.g. C_Dem_p) 5 for a total of 30 participants
    AC_n = 2 * N
    AC_p = 2 * N
    C_n = 2 * N
    C_p = 2 * N
    NO_n = 2 * N
    NO_p = 2 * N
    AC_Dem_p = AC_p // 2
    AC_Rep_p = AC_p // 2
    AC_Dem_n = AC_n // 2
    AC_Rep_n = AC_n // 2
    C_Dem_p = C_p // 2
    C_Rep_p = C_p // 2
    C_Dem_n = C_n // 2
    C_Rep_n = C_n // 2
    NO_Dem_p = NO_p // 2
    NO_Rep_p = NO_p // 2
    NO_Dem_n = NO_n // 2
    NO_Rep_n = NO_n // 2

class Subsession(BaseSubsession):
    pass

# Shuffle possible treatments [AC_n, C_n, AC_p, C_p, NO_n, NO_p: Anticonformist/Conformist, Nonpolitical/Political]


def creating_session(subsession):
    session = subsession.session
    session.AC_n = 0
    session.AC_p = 0
    session.C_n = 0
    session.C_p = 0
    session.NO_n = 0
    session.NO_p = 0
    session.AC_Dem_p = 0
    session.AC_Rep_p = 0
    session.AC_Dem_n = 0
    session.AC_Rep_n = 0
    session.C_Dem_p = 0
    session.C_Rep_p = 0
    session.C_Dem_n = 0
    session.C_Rep_n = 0
    session.NO_Dem_p = 0
    session.NO_Rep_p = 0
    session.NO_Dem_n = 0
    session.NO_Rep_n = 0    

    for player in subsession.get_players():
        # Initialize variables for the player
        player.participant.vars['training_attempt'] = 3 # Initialize training attempt
        player.participant.vars['failed_attention_check'] = False # Initialize attention check failure
        player.participant.vars['training_success'] = False # Initialize training success
        player.participant.vars['all_responses'] = {} # Initialize empty dictionary for all responses, will be appended on each round
        player.participant.vars['active'] = True # Initialize active status for the mock app later
        #player.participant.vars['single_group'] = False
        player.participant.vars['anticonformist'] = False
        player.participant.vars['complete_presurvey'] = True # Initialize completed status, will be set to False will be set to False if Training_3 fails or timeout_happened
        player.participant.vars['not_neutral'] = {} # Initialized to store if the player is not neutral in any scenario
        player.participant.vars['forced_response_counter'] = 0 # Initialize forced response counter
def no_nudge(player):
    if player.participant.treatment in ['AC_n', 'AC_p', 'C_n', 'C_p']:
        return False
    elif player.participant.treatment in ['NO_n', 'NO_p']:
        return True

def scenario_type(player):
    if player.participant.treatment in ['AC_n', 'C_n', 'NO_n']:
        return 'nonpolitical'
    elif player.participant.treatment in ['AC_p', 'C_p', 'NO_p']:
        return 'political'
      
class Group(BaseGroup):
    pass


class Player(BasePlayer):

    gives_consent = models.BooleanField(
        label="I acknowledge that I have read and understood the information above "
        "and confirm that I wish to participate in this study.")
    scenario_code = models.StringField()
    dropout = models.BooleanField(initial=False)

    # Training variables
    test_scenario = models.StringField(
    label="What do you think the community should do?",
    choices=[[-1, 'Against'],
            [0, 'Neutral'],
            [1, 'For']])
 
    dilemmatopic = models.BooleanField(
        label="The dilemma is about what the community should do with the lost cat.",
        choices=[
            [True, 'True'],
            [False, 'False'],
        ])
    majority = models.BooleanField(
        label="The majority of your neighbors are in favor of helping to search for the cat in the sewage.",
        choices=[
            [True, 'True'], 
            [False, 'False'],
        ])
    howmanyneighbors = models.BooleanField(
        label="You have 2 neighbors in your group.",
        choices=[
            [False, 'True'],# inverse the values since the correct answer is False
            [True, 'False'],
        ])

    total_correct = models.IntegerField()
    training_counter = models.IntegerField(initial=0) # Counter for training attempts, used to limit the number of attempts
    # Attention check
    attention_check = models.IntegerField(
    label="Which of the following is a vegetable?",
    choices=[
        [1, 'Salmon'],
        [2, 'Broccoli'],
        [3, 'Cheeseburger'],
        [4, 'Pizza'],
        [5, 'Milk'],
    ],
    widget=widgets.RadioSelectHorizontal,)
    
    # Demographics
    age = models.IntegerField(label='How old are you?', min=18, max=100)
    gender = models.StringField(choices=[['Man', 'Man'], 
                                         ['Woman', 'Woman'],
                                         ['Other', 'Other'],
                                         ['Prefer not to say', 'Prefer not to say']],
                                         label='What is your gender?',
                                         widget=widgets.RadioSelect,)
    
    education_lvl = models.StringField(
        choices=[['Less than high school', 'Less than high school'],
                ['High school diploma or equivalent', 'High school diploma or equivalent'],
                ['University degree or more', 'University degree or more']],
        label='What is the highest level of education you have completed?',
        widget=widgets.RadioSelect,)

    neighborhood_type = models.StringField(
        choices=[['Urban', 'Urban'],
                ['Suburban', 'Suburban (residential neighbourhood on the outskirts of a city or town)'],
                ['Countryside', 'Countryside (rural areas)']],
        label='What type of neighborhood do you live in?',
        widget=widgets.RadioSelect,)

    # Scenario response
    response = models.IntegerField(label="What do you think the community should do?",
                                   choices=[[-1, 'Against'],
                                           [0, 'Neutral'],
                                           [1, 'For']],
                                  widget=widgets.RadioSelectHorizontal())

    # Covariates
    def make_field(label):
        return models.IntegerField(
            choices=[[1, 'Strongly Disagree'],
            [2, 'Disagree'],
            [3, 'Neutral'],
            [4, 'Agree'],
            [5, 'Strongly Agree']],
            label=label,
            widget=widgets.RadioSelect,
            #blank=True, # Remove this to make it mandatory, this is done for testing purposes
        )
    

    political_charge = make_field("The situation described in the dilemma is politically controversial.")
    emotional_charge = make_field("The situation described in the dilemma is emotionally charged.")

    # To assign treatments equally across the political spectrum
    political_affiliation = models.StringField(label="In general, what is your political affiliation?",
        choices=[['Democrat','Democrat'],
                 ['Republican','Republican']],
                 widget=widgets.RadioSelectHorizontal())


# PAGES
class Introduction(Page):
    form_model = 'player'
    form_fields = ['gives_consent']

    @staticmethod
    def is_displayed(player:Player):
        return player.round_number == 1 
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.gives_consent = player.gives_consent
        player.participant.complete_presurvey = player.participant.gives_consent # Assigning active status based on consent
 
   
class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender','education_lvl', 'neighborhood_type', 'political_affiliation'] 

    @staticmethod
    def is_displayed(player:Player):
        return player.round_number == 1 and player.participant.complete_presurvey

class NeighborhoodInstruction(Page):
    @staticmethod
    def is_displayed(player:Player):
        return player.round_number == 1 and player.participant.complete_presurvey 
    

class Training(Page):
    form_model='player'
    form_fields = ['test_scenario']

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.complete_presurvey 


class TrainingNeighbor_1(Page):
    form_model='player'

    @staticmethod
    def get_form_fields(player:Player):  
        form_fields = ['dilemmatopic', 'majority', 'howmanyneighbors']
        random.shuffle(form_fields)  
        return form_fields
    
    @staticmethod
    def vars_for_template(player: Player):
        # Some made up responses of other players' to be displayed
        return dict(
            others_responses = [-1,1,1],
            scenario_title = "The Lost Cat",
            scenario_against = "Do not help with the search",
            scenario_neutral = "Verify the cat in the garden",
            scenario_for = "Help search near the sewage",
        )
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        total_correct = np.sum([player.dilemmatopic, 
                                player.majority, 
                                player.howmanyneighbors])
        if total_correct != 3:
            player.participant.vars['training_attempt'] -= 1
        else:
            player.participant.vars['training_success'] = True
        #print(f"Before next Training attempt: {player.participant.vars['training_attempt']}, {player.participant.vars['training_success']}")
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.complete_presurvey 
        # return player.participant.training_attempt == 3 and not player.participant.training_success and player.round_number == 1 and not player.participant.failed_attention_check and player.participant.gives_consent


class TrainingNeighbor_2(Page):
    form_model='player'
    #form_fields = ['dilemmatopic', 'majority', 'howmanyneighbors']
    @staticmethod
    def get_form_fields(player:Player):  
        form_fields = ['dilemmatopic', 'majority', 'howmanyneighbors']
        random.shuffle(form_fields)  
        return form_fields
    
    @staticmethod
    def vars_for_template(player: Player):
        # Some made up responses of other players' to be displayed
        return dict(
            others_responses = [-1,1,1],
            scenario_title = "The Lost Cat",
            scenario_against = "Do not help with the search",
            scenario_neutral = "Verify the cat in the garden",
            scenario_for = "Help search near the sewage",
        )
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        total_correct = np.sum([player.dilemmatopic, 
                                player.majority, 
                                player.howmanyneighbors])
        if total_correct != 3:
            player.participant.vars['training_attempt'] -= 1
        else:
            player.participant.vars['training_success'] = True
        #print(f"Training attempt: {player.participant.vars['training_attempt']}, {player.participant.vars['training_success']}")

    @staticmethod
    def is_displayed(player):
        #print(f"Round:{player.round_number} and Training Counter: {player.participant.vars['training_attempt']}")
        if player.round_number == 1 and player.participant.complete_presurvey:
            return player.participant.training_attempt == 2 and not player.participant.training_success


class AttentionCheck(Page):
    form_model = 'player'
    form_fields = ['attention_check']
    timeout_seconds = 60 # Set a timeout for the attention check
    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.participant.failed_attention_check = True # initially False
            player.participant.complete_presurvey = False # initially True
        else:
            if player.attention_check != 2: # wrong answer
               player.participant.failed_attention_check = True 
               player.participant.complete_presurvey = False

    @staticmethod
    def is_displayed(player:Player):
        if player.round_number == 1 and player.participant.complete_presurvey:
            return player.participant.training_attempt == 1 and not player.participant.training_success
    

class TrainingNeighbor_3(Page):
    form_model='player'

    @staticmethod
    def get_form_fields(player:Player):  
        form_fields = ['dilemmatopic', 'majority', 'howmanyneighbors']
        random.shuffle(form_fields)  
        return form_fields
    
    @staticmethod
    def vars_for_template(player: Player):
        # Some made up responses of other players' to be displayed
        return dict(
            others_responses = [-1,1,1],
            scenario_title = "The Lost Cat",
            scenario_against = "Do not help with the search",
            scenario_neutral = "Verify the cat in the garden",
            scenario_for = "Help search near the sewage",
        )
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        total_correct = np.sum([player.dilemmatopic, 
                                player.majority, 
                                player.howmanyneighbors])
        if total_correct != 3:
            player.participant.vars['training_attempt'] -= 1
            player.participant.complete_presurvey = False
        else:
            player.participant.vars['training_success'] = True
            player.participant.complete_presurvey = True

    @staticmethod
    def is_displayed(player):
        if player.round_number == 1 and player.participant.complete_presurvey:
            return player.participant.training_attempt == 1 


class ExperimentInstruction(Page):
    @staticmethod
    def before_next_page(player, timeout_happened):
        # Get player's political affiliation to determine treatment
        player.participant.political_affiliation = player.political_affiliation
        
        # Assign based on AC quotas and count on political affiliation quotas (only counting the political, because it's mirrored)
        available_treatments = []

        # Check quotas for AC and C treatments
        if player.participant.political_affiliation == 'Democrat':
            if player.subsession.session.AC_Dem_p < C.AC_Dem_p:
                available_treatments.append('AC_p')
            if player.subsession.session.C_Dem_p < C.C_Dem_p:
                available_treatments.append('C_p')
            if player.subsession.session.NO_Dem_p < C.NO_Dem_p:
                available_treatments.append('NO_p')
            if player.subsession.session.AC_Dem_n < C.AC_Dem_n:
                available_treatments.append('AC_n')
            if player.subsession.session.C_Dem_n < C.C_Dem_n:
                available_treatments.append('C_n')
            if player.subsession.session.NO_Dem_n < C.NO_Dem_n:
                available_treatments.append('NO_n')
        elif player.participant.political_affiliation == 'Republican':
            if player.subsession.session.AC_Rep_p < C.AC_Rep_p:
                available_treatments.append('AC_p')
            if player.subsession.session.C_Rep_p < C.C_Rep_p:
                available_treatments.append('C_p')
            if player.subsession.session.NO_Rep_p < C.NO_Rep_p:
                available_treatments.append('NO_p')
            if player.subsession.session.AC_Rep_n < C.AC_Rep_n:
                available_treatments.append('AC_n')
            if player.subsession.session.C_Rep_n < C.C_Rep_n:
                available_treatments.append('C_n')
            if player.subsession.session.NO_Rep_n < C.NO_Rep_n:
                available_treatments.append('NO_n')

        # Randomly select a treatment from the available options
        player.participant.treatment = random.choice(available_treatments)

        # Update the session's treatment counts
        if player.participant.treatment == 'AC_p':
            player.subsession.session.AC_p += 1
            if player.participant.political_affiliation == 'Democrat':
                player.subsession.session.AC_Dem_p += 1
            else:
                player.subsession.session.AC_Rep_p += 1
        elif player.participant.treatment == 'C_p':
            player.subsession.session.C_p += 1
            if player.participant.political_affiliation == 'Democrat':
                player.subsession.session.C_Dem_p += 1
            else:
                player.subsession.session.C_Rep_p += 1
        elif player.participant.treatment == 'NO_p':
            player.subsession.session.NO_p += 1
            if player.participant.political_affiliation == 'Democrat':
                player.subsession.session.NO_Dem_p += 1
            else:
                player.subsession.session.NO_Rep_p += 1
        elif player.participant.treatment == 'AC_n':
            player.subsession.session.AC_n += 1
            if player.participant.political_affiliation == 'Democrat':
                player.subsession.session.AC_Dem_n += 1
            else:
                player.subsession.session.AC_Rep_n += 1
        elif player.participant.treatment == 'C_n':
            player.subsession.session.C_n += 1
            if player.participant.political_affiliation == 'Democrat':
                player.subsession.session.C_Dem_n += 1
            else:
                player.subsession.session.C_Rep_n += 1
        elif player.participant.treatment == 'NO_n':
            player.subsession.session.NO_n += 1
            if player.participant.political_affiliation == 'Democrat':
                player.subsession.session.NO_Dem_n += 1
            else:
                player.subsession.session.NO_Rep_n += 1

        # Assign anticonformist status based on treatment
        player.participant.anticonformist = (player.participant.treatment in ['AC_n', 'AC_p'])

        # Debugging output
        print(f"Assigned treatment: {player.participant.treatment}, AC: {player.participant.anticonformist}")
        print(f"AC_p: {player.subsession.session.AC_p}, AC_n: {player.subsession.session.AC_n}, C_p: {player.subsession.session.C_p}, C_n: {player.subsession.session.C_n}, AC_Dem_p: {player.subsession.session.AC_Dem_p}, AC_Rep_p: {player.subsession.session.AC_Rep_p}, AC_Dem_n: {player.subsession.session.AC_Dem_n}, AC_Rep_n: {player.subsession.session.AC_Rep_n}, C_Dem_p: {player.subsession.session.C_Dem_p}, C_Rep_p: {player.subsession.session.C_Rep_p}, C_Dem_n: {player.subsession.session.C_Dem_n}, C_Rep_n: {player.subsession.session.C_Rep_n}")

        # Assign treatment to the player
        player.participant.vars['scenario_type'] = scenario_type(player) 
        player.participant.vars['no_nudge'] = no_nudge(player)

        if player.participant.scenario_type == 'nonpolitical':
            chosen_scenarios = C.SCENARIOS[0:3]
        elif player.participant.scenario_type == 'political':
            chosen_scenarios = C.SCENARIOS[3:6]

        # Shuffle and assign scenarios to the player    
        random.shuffle(chosen_scenarios)  
        player.participant.vars['scenario_order'] = chosen_scenarios


    @staticmethod
    def is_displayed(player:Player):
        return player.participant.complete_presurvey and player.round_number == 1

class Scenario(Page):
    form_model = 'player'
    form_fields = ['political_charge', 'emotional_charge', 'response']

    @staticmethod
    def vars_for_template(player: Player):
        # Access the scenario based on the randomized order
        scenario = player.participant.vars['scenario_order'][player.round_number - 1]
        
        return dict(
            scenario_text = scenario['Text'],
            scenario_title = scenario['Title'],
            scenario_code = scenario['code'],
            scenario_against = scenario['Against'],
            scenario_neutral = scenario['Neutral'],
            scenario_for = scenario['For'],
        )
    def before_next_page(player: Player, timeout_happened):
        # Get the current scenario code
        player.scenario_code = player.participant.vars['scenario_order'][player.round_number - 1]['code']
        
        # Store the response in the participant's vars 
        player.participant.vars['all_responses'][player.scenario_code] = player.response
        # Combine all participants' all_responses dictionaries into a session-level variable
        if 'combined_responses' not in player.session.vars:
            player.session.vars['combined_responses'] = {}
            # Add the current player's all_responses dictionary to the combined dictionary
        
        player.session.vars['combined_responses'][player.participant.code] = player.participant.vars['all_responses']
        
        # In the last round, check whether the player is eligible for the discussion
        if player.round_number == C.NUM_ROUNDS:
            # Record any not neutral responses into a dictionary with scenario codes as the key and save it to the participant's vars not_neutral
            player.participant.vars['not_neutral'] = {
                code: response for code, response in player.participant.vars['all_responses'].items() if response != 0
            }
            print(f"Not neutral responses for {player.participant.code}: {player.participant.not_neutral}")

            
    @staticmethod
    def is_displayed(player:Player):
        return player.participant.gives_consent and player.participant.complete_presurvey and player.round_number <= C.NUM_ROUNDS 

# Full page sequence for pilot 
page_sequence = [Introduction, Demographics, NeighborhoodInstruction, Training, TrainingNeighbor_1, 
                 TrainingNeighbor_2, AttentionCheck, TrainingNeighbor_3, ExperimentInstruction,
                 Scenario]

# # Page sequence for testing purposes
# page_sequence = [Introduction, Demographics, TrainingNeighbor_1, 
#                  TrainingNeighbor_2, AttentionCheck, TrainingNeighbor_3,ExperimentInstruction,
#                  Scenario,]
