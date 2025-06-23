from otree.api import *
import pandas as pd
import numpy as np
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
    # all scenarios: not used for the Prolific, but only used for the Collective Minds' app
    CSV = open_CSV('presurvey/20250512_scenarios-new.csv')
    SCENARIOS = CSV.to_dict(orient='records')
    #NUM_ROUNDS = len(CSV['code']) # number of scenarios
    # for testing: 
    NUM_ROUNDS = 4



class Subsession(BaseSubsession):
    pass


def creating_session(subsession):
    for player in subsession.get_players():
        # Shuffle the scenario order for each player
        shuffled_scenarios = random.sample(C.SCENARIOS, len(C.SCENARIOS))
        player.participant.vars['scenario_order'] = shuffled_scenarios  # Store the shuffled order as a participant variable
        player.participant.vars['training_attempt'] = 3 # Initialize training attempt
        player.participant.vars['failed_attention_check'] = False # Initialize attention check failure
        player.participant.vars['training_success'] = False # Initialize training success
        player.participant.vars['all_responses'] = {} # Initialize empty dictionary for all responses, will be appended on each round
        
        
class Group(BaseGroup):
    print("Creating group")


class Player(BasePlayer):
    gives_consent = models.BooleanField(
        label="I acknowledge that I have read and understood the information above "
        "and confirm that I wish to participate in this study.")
    scenario_code = models.StringField()
    dropout = models.BooleanField(initial=False)

    # Training variables
    test_scenario = models.StringField(
    label="What do you think the community should do?",
    choices=[['Do not help with the search', 'Do not help with the search'],
            ['Verify the cat in the garden', 'Verify the cat in the garden'],
            ['Help search near the sewage', 'Help search near the sewage']],
    widget=widgets.RadioSelectHorizontal())
 
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
    ])
    
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
            blank=True, # Remove this to make it mandatory, this is done for testing purposes
        )
    
    attitude_certainty = make_field("I am certain about my position on this issue.")   
    likelihood = make_field("This dilemma is likely to happen in a neighborhood.")
    political_charge = make_field("The situation described in the dilemma is politically controversial.")
    emotional_charge = make_field("The situation described in the dilemma is emotionally charged.")
    disagree_conform = make_field("I will change my mind if most people in my neighborhood disagreed with my position.")
    

    # # Other feedback
    # feedback = models.LongStringField(label=
    #                                   "Do you have any comments on this dilemma or the solutions offered? If no, click next",
    #                                   blank=True)
    # feedback_final = models.LongStringField(label="Please provide your feedback here:")


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
 
   
class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender','education_lvl', 'neighborhood_type'] 

    @staticmethod
    def is_displayed(player:Player):
        return player.round_number == 1 and player.participant.gives_consent
    

class Neighborhood(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player:Player):
        return player.round_number == 1 and player.participant.gives_consent 


class NeighborhoodInstruction(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player:Player):
        return player.round_number == 1 and player.participant.gives_consent 
    

class Training(Page):
    form_model='player'
    form_fields = ['test_scenario']

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.gives_consent 


class TrainingNeighbor_1(Page):
    form_model='player'
    form_fields = ['dilemmatopic', 'majority', 'howmanyneighbors']

    @staticmethod
    def vars_for_template(player: Player):
        # Some made up responses of other players' to be displayed
        return dict(
            others_responses = [-1,1,1,1],
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
            player.participant.active = "active"
        #print(f"Before next Training attempt: {player.participant.vars['training_attempt']}, {player.participant.vars['training_success']}")
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.gives_consent 
        # return player.participant.training_attempt == 3 and not player.participant.training_success and player.round_number == 1 and not player.participant.failed_attention_check and player.participant.gives_consent


class TrainingNeighbor_2(Page):
    form_model='player'
    form_fields = ['dilemmatopic', 'majority', 'howmanyneighbors']
    
    @staticmethod
    def vars_for_template(player: Player):
        # Some made up responses of other players' to be displayed
        return dict(
            others_responses = [-1,1,1,1],
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
            player.participant.active = "active"
        #print(f"Training attempt: {player.participant.vars['training_attempt']}, {player.participant.vars['training_success']}")

    @staticmethod
    def is_displayed(player):
        #print(f"Round:{player.round_number} and Training Counter: {player.participant.vars['training_attempt']}")
        if player.round_number == 1 and player.participant.gives_consent:
            return player.participant.training_attempt == 2 and not player.participant.training_success


class AttentionCheck(Page):
    form_model = 'player'
    form_fields = ['attention_check']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.participant.vars['failed_attention_check'] = True 
            player.participant.active = "inactive"
        else:
            if player.attention_check != 2: # wrong answer
               player.participant.vars['failed_attention_check'] = True 
               player.participant.active = "inactive"
               #print("Attention check not passed")
            else:
                player.participant.vars['failed_attention_check'] = False 
                #print("Attention check passed")
                player.participant.active = "active"

    @staticmethod
    def is_displayed(player:Player):
        #print(f"Round:{player.round_number} and Training Counter: {player.participant.vars['training_attempt']}")
        if player.round_number == 1 and player.participant.gives_consent:
            return player.participant.training_attempt == 1 and not player.participant.training_success
        #player.participant.training_attempt == 1 and not player.participant.training_success and player.round_number == 1 and not player.participant.failed_attention_check and player.participant.gives_consent
    

class TrainingNeighbor_3(Page):
    form_model='player'
    form_fields = ['dilemmatopic', 'majority', 'howmanyneighbors']
    
    @staticmethod
    def vars_for_template(player: Player):
        # Some made up responses of other players' to be displayed
        return dict(
            others_responses = [-1,1,1,1],
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
            player.participant.active = "inactive"
        else:
            player.participant.vars['training_success'] = True
            player.participant.active = "active"
        #print(f"Training attempt: {player.participant.vars['training_attempt']}, {player.participant.vars['training_success']}")

    @staticmethod
    def is_displayed(player):
        #print(f"Round:{player.round_number} and Training Counter: {player.participant.vars['training_attempt']} and Training Success: {player.participant.training_success} and Failed Attention Check: {player.participant.failed_attention_check}")
        if player.round_number == 1 and player.participant.gives_consent and player.participant.active == "active":
            return player.participant.training_attempt == 1 


class Scenario(Page):
    form_model = 'player'
    form_fields = ['attitude_certainty', 'likelihood', 'political_charge', 'emotional_charge', 
                   'disagree_conform', 'response'] 

    @staticmethod
    def vars_for_template(player: Player):
        # Access the scenario based on the randomized order
        scenario = player.participant.vars['scenario_order'][player.round_number - 1]
        
        return dict(
            scenario_text = scenario['Text'],
            scenario_title = scenario['Title'],
            scenario_code = scenario['code'],
            scenario_against = scenario['Against'],
            scenario_for = scenario['For'],
        )
    def before_next_page(player: Player, timeout_happened):
        # Get the current scenario code
        player.scenario_code = player.participant.vars['scenario_order'][player.round_number - 1]['code']
        # Debug check:
        # print(f"Scenario code for round {player.round_number}: {player.scenario_code}")

        # Store the response in the participant's vars and record the time of waiting
        player.participant.vars['all_responses'][player.scenario_code] = player.response
        # Combine all participants' all_responses dictionaries into a session-level variable
        if 'combined_responses' not in player.session.vars:
            player.session.vars['combined_responses'] = {}
            # Add the current player's all_responses dictionary to the combined dictionary
        
        player.session.vars['combined_responses'][player.participant.code] = player.participant.vars['all_responses']

    @staticmethod
    def is_displayed(player:Player):
        return player.participant.gives_consent and player.participant.training_success and not player.participant.failed_attention_check and player.round_number <= C.NUM_ROUNDS 


class FinalPage(Page):
    form_model = 'player'
    timeout_seconds = 5
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS and player.participant.gives_consent and player.participant.training_success and not player.participant.failed_attention_check
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.wait_page_arrival = time.time()

    
class NoConsent(Page):
    form_model = 'player'
    form_fields = []
    timeout_seconds = 30
    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.gives_consent 
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.gives_consent = True
        if timeout_happened:
            player.dropout = True
            print(player.dropout)
        else:
            player.dropout = False
            print(player.dropout)


class ExitPage_TWO(Page):
    form_model = 'player'

    @staticmethod
    def js_vars(player):
        return dict(
            completionlink=player.subsession.session.config['completionlink']
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.gives_consent and player.round_number == C.NUM_ROUNDS

page_sequence = [Introduction, Demographics, Neighborhood, NeighborhoodInstruction, TrainingNeighbor_1, TrainingNeighbor_2,
                 AttentionCheck, TrainingNeighbor_3, Scenario, FinalPage]
