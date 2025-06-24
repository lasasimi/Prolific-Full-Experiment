from otree.api import *
import numpy as np # type: ignore
import json
import time
import random
import pandas as pd


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
    NUM_ROUNDS = 5
    MEDIUM_WAIT = 20  # 5 mins 
    LONG_WAIT = 5  # 10 mins 
    CSV = open_CSV('presurvey/dummy_4scenarios_n.csv')
    SCENARIOS = CSV.to_dict(orient='records')
    GROUPS = open_CSV('mock/beta_02_p_00_N_10.csv')


class Subsession(BaseSubsession):
    pass


def medium_wait(player):
    participant = player.participant
    return (time.time() - participant.wait_page_arrival) > C.MEDIUM_WAIT * 60  # in mins


def long_wait(player):
    participant = player.participant
    return time.time() - participant.wait_page_arrival > C.LONG_WAIT * 60  # in mins


def group_by_arrival_time_method(subsession, waiting_players):
    """
    REMEMBER TO INCLUDE A SELF LOAD EVERY 30 SECS OR SO, IF NO MORE PARTICIPANTS ENTER, CODE WONT EXECUTE 
    """
    session = subsession.session
    response = {}
    for p in waiting_players:
        response[p.participant.code] = p.participant.all_responses
    
    # Getting list of scenarios, always get first key, instead of relying on p.id_in_group == 1
    try:
        first_key = list(response.keys())[0] # fails if room is empty 
        scenarios = [key for key in response[first_key]]
    except:
        scenarios = []

    scenario_counts = {}
    for i_sce, sce in enumerate(scenarios):
        scenario_counts[sce] = {}
        scenario_counts[sce]['A'] = []
        scenario_counts[sce]['F'] = []

    for p in waiting_players:
        # print(p.id_in_group)
        for i_sce, sce in enumerate(scenarios):
            if response[p.participant.code][sce] == -1:
                scenario_counts[sce]['A'].append(p)
            else:
                scenario_counts[sce]['F'].append(p)
            # print(sce,"Faction A:", len(scenario_counts[sce]['A']), "Faction F:", len(scenario_counts[sce]['F']))

    # players waiting for more than 10 mins 
    long_waiting = [p for p in waiting_players if long_wait(p)]
    if len(long_waiting) >= 1:
        for player in long_waiting:
            print('Ready to let participant go, waiting for too long')
            return [player]
            break
    
    ##### BLOCK 0 #####
    if len(waiting_players) > 3: ##### TEST ONLY!! CHANGE LATER to 20/6 #####
        print('Ready to check discussion group')
        temp_scenarios = scenarios.copy()
        temp_scenarios = random.sample(temp_scenarios, len(temp_scenarios))
        # players waiting for more than 5 mins are considered of medium wait
        # medium_waiting = [p for p in waiting_players if medium_wait(p)]
        
        ##### BLOCK 1 #####
        for i_sce, sce in enumerate(temp_scenarios):
            print(len(scenario_counts[sce]['A']),len(scenario_counts[sce]['F']))
            if len(scenario_counts[sce]['A']) == 2 and len(scenario_counts[sce]['F']) == 2: ##### TEST ONLY!! CHANGE LATER to CORRECT 50/50#####
                group = scenario_counts[sce]['A']+scenario_counts[sce]['F']
                for p in group:
                    p.participant.scenario = sce  # setting a scenarioi group-level variable
                print('Ready to create a 50/50 group N=4')
                # print(sce,scenario_counts[sce]['A']+scenario_counts[sce]['F'])
                return group
                break

            """ 
            ##### BLOCK 2 #####
            elif len(medium_waiting) > 3:
                ##### TEST ONLY!! 80/20 OPTION CHANGE TO N = 10/4 ##### 
                if len(scenario_counts[sce]['A']) == 2 and len(scenario_counts[sce]['F']) == 2:
                    print('Ready to create a 50/50 group N=4')
                    print(sce,scenario_counts[sce]['A']+scenario_counts[sce]['F'])
                    return(scenario_counts[sce]['A']+scenario_counts[sce]['F'])
                    break
            else: # essentially does nothing — it just complete the if-elif-else structure, could ignore 
                pass
            """ 

    else: 
        print('not enough players yet to create a group')


class Group(BaseGroup):
    group_size = models.StringField(initial='single')
    is_group_single = models.BooleanField()
    

class Player(BasePlayer):
    scenario = models.StringField()
    discussion_grp = models.IntegerField()


# PAGES
class GroupingWaitPage(WaitPage):
    group_by_arrival_time = True
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.active 


class GroupSizeWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        session = group.subsession.session
        group_players = group.get_players()
        
        if len(group_players) == 6:
            group_size = 'N20'
            is_group_single = False
        elif len(group_players) == 4:
            group_size = 'N10'
            is_group_single = False
        else:
            group_size = 'single'
            is_group_single = True     

        # Save to the group model (for round 1 only)
        group.group_size = group_size
        group.is_group_single = is_group_single 

        # Save persistently to participant
        for p in group_players:
            p.participant.group_size = group_size
            p.participant.is_group_single = is_group_single
            if group_size == 'single':
                p.participant.single_group = True  # they go to the pay up, but no bonus payment 

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.active 


class DiscussionGRPWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        # Copy group_size from participant (set in round 1)
        example_player = group.get_players()[0]
        group.group_size = example_player.participant.group_size
        group.is_group_single = example_player.participant.is_group_single

        if group.group_size == 'N10':
            faction_A = [p.participant.code for p in group.get_players() if p.participant.all_responses[p.participant.scenario]==-1]
            faction_A = random.sample(faction_A,len(faction_A))
            faction_F = [p.participant.code  for p in group.get_players() if p.participant.all_responses[p.participant.scenario]==1]
            faction_F = random.sample(faction_F,len(faction_F))

            player_ids = {code: i + 1 for i, code in enumerate(faction_A + faction_F)}

            player_ids = {code: i + 1 for i, code in enumerate(faction_A)}
            player_ids = {code: i + 6 for i, code in enumerate(faction_F)}

            for p in group.get_players():
                p.participant.player_ids = player_ids
            
            for p in group.get_players():
                player_id = p.participant.player_ids[p.participant.code]
                row = C.GROUPS[C.GROUPS['Player_IDs'] == player_id]
                group_name = f'group_{p.round_number}'
                p.discussion_grp = int(row.iloc[0][group_name])  
    
    @staticmethod
    def is_displayed(player):
        return player.participant.active and not player.participant.single_group
            

class Discussion(Page):
    @staticmethod
    def vars_for_template(player: Player):
        # Get discussion partners for THIS player
        discussion_partners = [
            o for o in player.get_others_in_group() if o.discussion_grp == player.discussion_grp
        ]
        print("Player:",player.id_in_group, discussion_partners)

        return {'discussion_partners' : discussion_partners}

    @staticmethod
    def is_displayed(player):
        return player.participant.active and not player.participant.single_group


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [GroupingWaitPage, GroupSizeWaitPage, DiscussionGRPWaitPage, Discussion]
