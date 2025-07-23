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
    SCENARIOS = open_CSV('presurvey/3scenarios_pilot_np.csv').to_dict(orient='records')  # Convert to a list of dictionaries
    NEIGHBORS = open_CSV('mock/neighbors_configurations.csv').to_dict(orient='records')  # Convert to a list of dictionaries
    # MAX NUMBER OF FORCED RESPONSES 
    MAX_FORCED = 3 

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    scenario = models.StringField()
    discussion_grp = models.StringField()
    response = models.IntegerField(label="What do you think the community should do?",
                                   choices=[[-1, 'Against'],
                                            [0, 'Neutral'],
                                            [1, 'For']],
                                            widget=widgets.RadioSelectHorizontal())
    
    forced_response = models.BooleanField(initial=False)
    treatment = models.StringField() 



# PAGES
class GroupingWaitPage(Page): # this one has the image of neighbor discussion
    template_name = 'mock/GroupingWaitPage.html'
    timeout_seconds = 20

   # Assign the neighbor configurations to participants
    @staticmethod
    def vars_for_template(player):
        # Shuffle the neighbor configurations (rows)
        shuffled_neighbors = C.NEIGHBORS.copy()
        random.shuffle(shuffled_neighbors)  # Shuffle rows
        print(f"After row shuffle: {shuffled_neighbors}")

        # Shuffle the columns for each row
        for row in shuffled_neighbors:
            keys = list(row.keys())  # Get the column names (keys)
            random.shuffle(keys)  # Shuffle the column order
            shuffled_row = {key: row[key] for key in keys}  # Rebuild the row with shuffled keys
            row.clear()
            row.update(shuffled_row)  # Update the row with the shuffled order

        print(f"After column shuffle: {shuffled_neighbors}")

        # Assign the shuffled configurations to the participant
        player.participant.neighbors_configurations = shuffled_neighbors
        

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.complete_presurvey 


class DiscussionGRPWaitPage(Page): # round by round, call the row for the neighbors_configurations
    template_name = 'mock/DiscussionGRPWaitPage.html'
    timeout_seconds = random.randint(3,5)  # Random wait time between 3 and 5 seconds

    @staticmethod
    def is_displayed(player):
        return player.participant.complete_presurvey 
    
    @staticmethod
    def vars_for_template(player):    
        print(f"Participant does not have nudge is: {player.participant.no_nudge}")    
        return dict(
            anticonformist = player.participant.anticonformist,
            no_nudge = player.participant.no_nudge,  
        )
        

class Nudge(Page):
    timeout_seconds = 30 # to force proceed after 30 seconds of inactivity

    @staticmethod
    def vars_for_template(player):     
        return dict(
            anticonformist = player.participant.anticonformist,
            no_nudge = player.participant.no_nudge,  
        )
        
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.complete_presurvey and not player.participant.no_nudge


class Discussion(Page):
    def get_timeout_seconds(player):
        if player.round_number == 1:
            return 90  # longer seconds for the first round
        elif 2 <= player.round_number <= 4:
            return 45
        else:
            return 30
        
    form_model = 'player'
    form_fields = ['response']

    @staticmethod
    def vars_for_template(player): 
        if player.round_number == 1:
            if player.participant.vars['not_neutral']:
                # Choose a random scenario code from the not neutral responses
                player.participant.scenario = random.choice(list(player.participant.vars['not_neutral'].keys()))
            elif player.participant.vars['not_neutral'] == {}:
                print(f"not_neutral is empty. Choosing one randomly from scenario_order: {player.participant.vars['scenario_order']}")
                # If not_neutral is empty, choose a scenario based on the scenario_type
            scenario_codes = [scenario['code'] for scenario in player.participant.vars['scenario_order']]
            player.participant.scenario = random.choice(scenario_codes)
            print(f"Chosen scenario from scenario_order: {player.participant.scenario}")
        
        # Find the scenario row where the 'code' matches player.participant.scenario
        row = next((scenario for scenario in C.SCENARIOS if scenario['code'] == player.participant.scenario), None)
        
        # Get the neighbors for the current round
        neighbors_current = player.participant.neighbors_configurations[player.round_number - 1]
        # Extract all keys starting with "neighbor" and get their values
        player.participant.neighbors = [neighbors_current[key] for key in neighbors_current if key.startswith("neighbor")]
        print(f"Neighbors for round {player.round_number}: {player.participant.neighbors}")

        return dict(
            scenario_title=row['Title'],
            scenario_text=row['Text'],
            scenario_against=row['Against'],
            scenario_neutral=row['Neutral'],
            scenario_for=row['For'],
            others_responses=player.participant.neighbors,
            anticonformist=player.participant.anticonformist,
            no_nudge=player.participant.no_nudge,
        )
    
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        print(f"Timeout counter: {player.participant.forced_response_counter}")
        if timeout_happened:
            player.forced_response = True 
            player.response = random.choice([-1, 0, 1])
            player.participant.forced_response_counter += 1
            if player.participant.forced_response_counter > C.MAX_FORCED:
                player.participant.active = False 
        if not player.participant.active:
            player.participant.complete_presurvey = False

    @staticmethod
    def is_displayed(player):
        print(f"Debug: Bot is {player.participant.code}, on round {player.round_number}")
        return player.participant.complete_presurvey

page_sequence = [GroupingWaitPage, DiscussionGRPWaitPage, Nudge, Discussion]
