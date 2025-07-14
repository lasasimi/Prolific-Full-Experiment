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
    NUM_ROUNDS = 20 
    MEDIUM_WAIT = 20  ##### CONSIDER REMOVING !!!!! 
    LONG_WAIT = 10  # SHORTEN? 10 mins !!!!! 
    N_TEST = 10 #### N=10
    CSV = open_CSV('presurvey/dummy_4scenarios_n.csv') ### REVIEW TO DELETE IF POSSIBLE
    SCENARIOS = open_CSV('presurvey/dummy_4scenarios_n.csv')
    GROUPS = open_CSV('mock/beta_02_p_02_N_10.csv')
    # player.subsession.session.config['beta']
    # player.subsession.session.config['p']

class Subsession(BaseSubsession):
    pass


def medium_wait(player):
    participant = player.participant
    return (time.time() - participant.wait_page_arrival) > C.MEDIUM_WAIT * 60  # in mins


def long_wait(player):
    participant = player.participant
    return time.time() - participant.wait_page_arrival > C.LONG_WAIT * 60  # in mins


def group_by_arrival_time_method(subsession, waiting_players):
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

    # players waiting for more than 10 mins 
    long_waiting = [p for p in waiting_players if long_wait(p)]
    if len(long_waiting) >= 1:
        for player in long_waiting:
            print('Ready to let participant go, waiting for too long')
            return [player]
            #break
    
    ##### BLOCK 0 #####
    if len(waiting_players) >= C.N_TEST: ##### TEST ONLY!! CHANGE LATER to 10/4 #####
        print('Ready to check discussion group')
        temp_scenarios = scenarios.copy()
        temp_scenarios = random.sample(temp_scenarios, len(temp_scenarios))
        # players waiting for more than 5 mins are considered of medium wait
        # medium_waiting = [p for p in waiting_players if medium_wait(p)]
        
        ##### BLOCK 1 #####
        for i_sce, sce in enumerate(temp_scenarios):
            if len(scenario_counts[sce]['A']) == C.N_TEST/2 and len(scenario_counts[sce]['F']) == C.N_TEST/2: ##### TEST ONLY!! CHANGE LATER to CORRECT 50/50#####
                print('Ready to create a 50/50 group N=4')
                group = scenario_counts[sce]['A']+scenario_counts[sce]['F']
                for p in group:
                    p.participant.scenario = sce  # setting a scenarioi group-level variable
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


# PAGES
class GroupingWaitPage(WaitPage):
    template_name = 'mock/GroupingWaitPage.html'
    group_by_arrival_time = True
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.active 


class GroupSizeWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        session = group.subsession.session
        group_players = group.get_players()
        
        if len(group_players) == 20:
            group_size = 'N20'
            is_group_single = False
        elif len(group_players) == C.N_TEST:
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
    template_name = 'mock/DiscussionGRPWaitPage.html'
    @staticmethod
    def after_all_players_arrive(group: Group):
        # Copy group_size from participant (set in round 1)
        example_player = group.get_players()[0]
        group.group_size = example_player.participant.group_size
        group.is_group_single = example_player.participant.is_group_single

        if group.subsession.round_number == 1:
            if group.group_size == 'N10':
                
                faction_A = [p.participant.code for p in group.get_players() if p.participant.all_responses[p.participant.scenario]==-1]
                faction_A = random.sample(faction_A,len(faction_A))
                faction_F = [p.participant.code  for p in group.get_players() if p.participant.all_responses[p.participant.scenario]==1]
                faction_F = random.sample(faction_F,len(faction_F))

                player_ids = {code: i + 1 for i, code in enumerate(faction_A)}
                player_ids.update({code: i + 6 for i, code in enumerate(faction_F)})  # Add F starting at 6

                for p in group.get_players():
                    p.participant.player_ids = player_ids

                    player_id = p.participant.player_ids[p.participant.code]
                    row = C.GROUPS[C.GROUPS['Player_IDs'] == player_id]

                    if int(row.iloc[0]['Anticonformists']) == 1:
                        p.participant.anticonformist = True
            
        for p in group.get_players():
            player_id = p.participant.player_ids[p.participant.code]
            row = C.GROUPS[C.GROUPS['Player_IDs'] == player_id]
            group_name = f'group_{p.round_number}'
            p.discussion_grp = int(row.iloc[0][group_name])  

            if p.participant.all_responses[p.participant.scenario] == -1:
                p.participant.position = 'Against'
            else:
                p.participant.position = 'For'
        
        if group.subsession.round_number == 1:
            for p in group.get_players():
                p.old_response = p.participant.all_responses[p.participant.scenario]
        else:
            for p in group.get_players():
                p.old_response = p.in_round(p.round_number - 1).new_response

    @staticmethod
    def is_displayed(player):
        return player.participant.active and not player.participant.single_group


class Phase3(Page):
    timeout_seconds = 45 # to force proceed after 30 seconds of inactivity
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.active and not player.participant.single_group    


class Nudge(Page):
    timeout_seconds = 45 # to force proceed after 30 seconds of inactivity
    @staticmethod
    def vars_for_template(player):        
        return dict(
            anticonformist = player.participant.anticonformist,
        )
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.active and not player.participant.single_group


class Discussion(Page):
    def get_timeout_seconds(player):
        if player.round_number == 1:
            return 90  # longer seconds for the first round
        elif 2<= player.round_number <= 4:
            return 45
        else:
            return 30
        
    form_model = 'player'
    form_fields = ['new_response']

    @staticmethod
    def vars_for_template(player):  
        print(player.participant.scenario)
        print(C.SCENARIOS)
        row = C.SCENARIOS[C.SCENARIOS['code']==player.participant.scenario]

        discussion_partners = [o for o in player.get_others_in_group() if o.discussion_grp == player.discussion_grp]   
        return dict(
            scenario_title = row.iloc[0]['Title'],
            scenario_text = row.iloc[0]['Text'],
            scenario_against = row.iloc[0]['Against'],
            scenario_neutral = row.iloc[0]['Neutral'],
            scenario_for = row.iloc[0]['For'],
            others_responses = [other.old_response for other in discussion_partners if other.id_in_group != player.id_in_group],
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
        return player.participant.active and not player.participant.single_group


page_sequence = [GroupingWaitPage, GroupSizeWaitPage, DiscussionGRPWaitPage, Phase3, Nudge, Discussion]
