from otree.api import *
import numpy as np # type: ignore
import json
import time
import random
import pandas as pd # type: ignore


doc = """
Your app description
"""
def open_CSV(filename):
    """
    :param filename: opinions.csv
    :return: a list of statements for the session
    """
    temp = pd.read_csv(filename, sep=',')
    return temp


class C(BaseConstants):
    NAME_IN_URL = 'mock'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10 # FOR PRETEST TWO, PREVIOUSLY 5 
    MEDIUM_WAIT = 6  # IF A DISCUSSION GROUP HASN'T BEEN FORMED BY THEN, CHECK FOR OTHER GROUP SIZES 
    LONG_WAIT = 10  # IF NO GROUP HAS BEEN FORMED, LET GO AND PAY WAITING BONUS 
    N_TEST = 8 # SIZE OF DISCUSSION GROUP 
    # CSV = open_CSV('presurvey/dummy_4scenarios_n.csv') ### TK (GJ): REVIEW TO DELETE IF POSSIBLE
    SCENARIOS = open_CSV('presurvey/3scenarios_pilot_np.csv')
    NEIGHBORS = open_CSV('mock/neighbors_configurations.csv').to_dict(orient='records')  # Convert to a list of dictionaries

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass
    # group_size = models.StringField(initial='single')
    # is_group_single = models.BooleanField()
    # beta_50 = models.BooleanField()  # for beta 0.50 treatment
    # anti_prop = models.StringField()  # for p value treatment

class Player(BasePlayer):
    scenario = models.StringField()
    discussion_grp = models.StringField()
    old_response = models.IntegerField(label="What do you think the community should do?",
                                   choices=[[-1, 'Against'],
                                            [0, 'Neutral'],
                                            [1, 'For']],
                                            widget=widgets.RadioSelectHorizontal())
    new_response = models.IntegerField(label="What do you think the community should do?",
                                   choices=[[-1, 'Against'],
                                            [0, 'Neutral'],
                                            [1, 'For']],
                                            widget=widgets.RadioSelectHorizontal())
    forced_response = models.BooleanField(initial=False)
    treatment = models.StringField() 


# PAGES
class GroupingWaitPage(Page): # this one has the image of neighbor discussion
    template_name = 'mock/GroupingWaitPage.html'
    timeout_seconds = 10

   # Assign the neighbor configurations to participants
    @staticmethod
    def vars_for_template(player):
        # Shuffle the neighbor configurations
        player.participant.neighbors_configurations = C.NEIGHBORS.copy()
        print(f"Before shuffle: {player.participant.neighbors_configurations}")
        random.shuffle(player.participant.neighbors_configurations)
        print(f"After shuffle: {player.participant.neighbors_configurations}")
        # Save to a participant field
        player.participant.neighbors_configurations = player.participant.neighbors_configurations

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.complete_presurvey 


class DiscussionGRPWaitPage(Page): # round by round, call the row for the neighbors_configurations
    template_name = 'mock/DiscussionGRPWaitPage.html'
    timeout_seconds = random.randint(3,10)  # Random wait time between 3 and 10 seconds

    @staticmethod
    def is_displayed(player):
        return player.participant.complete_presurvey 

class Nudge(Page):
    timeout_seconds = 30 # to force proceed after 30 seconds of inactivity
    @staticmethod
    def vars_for_template(player):        
        return dict(
            anticonformist = player.participant.anticonformist,
        )
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.complete_presurvey 


class Discussion(Page):
    def get_timeout_seconds(player):
        if player.round_number == 1:
            return 90  # longer seconds for the first round
        elif 2 <= player.round_number <= 4:
            return 45
        else:
            return 30
        
    form_model = 'player'
    form_fields = ['new_response']

    @staticmethod
    def vars_for_template(player): 
        # if not_neutral consists of more than 1 scenario code, then choose one randomly, if it is empty, then choose  randomly based on the scenario_type
        if player.participant.vars['not_neutral']:
            # Choose a random scenario code from the not neutral responses
            scenario_code = random.choice(list(player.participant.vars['not_neutral'].keys()))
            player.participant.scenario = scenario_code
        else:
            # If not_neutral is empty, choose a scenario based on the scenario_type
            if player.participant.scenario_type == 'nonpolitical':
                player.participant.scenario = random.choice(player.participant.vars['scenario_order'])
            elif player.participant.scenario_type == 'political':
                player.participant.scenario = random.choice(player.participant.vars['scenario_order'])

        # if player.participant.scenario_type == 'nonpolitical':
        #     player.participant.scenario = 's2_n'  # Example scenario code for non-political
        # elif player.participant.scenario_type == 'political':
        #     player.participant.scenario = 's2_p'

        neighbors_current = player.participant.neighbors_configurations[player.round_number - 1]
       # Extract all keys starting with "neighbor" and get their values
        player.participant.neighbors = [
        neighbors_current[key] for key in neighbors_current if key.startswith("neighbor")]

        print(f"Neighbors for round {player.round_number}: {player.participant.neighbors}")
        row = C.SCENARIOS[C.SCENARIOS['code']==player.participant.scenario]

        return dict(
            scenario_title = row.iloc[0]['Title'],
            scenario_text = row.iloc[0]['Text'],
            scenario_against = row.iloc[0]['Against'],
            scenario_neutral = row.iloc[0]['Neutral'],
            scenario_for = row.iloc[0]['For'],
            others_responses = player.participant.neighbors,
            anticonformist = player.participant.anticonformist,
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            ### REVIEW THE RULE #### 
            player.forced_response = True # only in the last round, make them inactive
            player.new_response = random.choice([-1, 0, 1])

    @staticmethod
    def is_displayed(player):
        print(f"Debug: Bot is {player.participant.code}, on round {player.round_number}")
        return player.participant.complete_presurvey

page_sequence = [GroupingWaitPage, DiscussionGRPWaitPage, Nudge, Discussion]
