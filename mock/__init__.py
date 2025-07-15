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
    NUM_ROUNDS = 20 # FOR PRETEST TWO, PREVIOUSLY 5 
    MEDIUM_WAIT = 6  # IF A DISCUSSION GROUP HASN'T BEEN FORMED BY THEN, CHECK FOR OTHER GROUP SIZES 
    LONG_WAIT = 10  # IF NO GROUP HAS BEEN FORMED, LET GO AND PAY WAITING BONUS 
    N_TEST = 8 # SIZE OF DISCUSSION GROUP 
    # CSV = open_CSV('presurvey/dummy_4scenarios_n.csv') ### TK (GJ): REVIEW TO DELETE IF POSSIBLE
    SCENARIOS = open_CSV('presurvey/4scenarios_np.csv')
    # GROUPS = open_CSV('mock/beta_02_p_02_N_10.csv')
    # SETTING REQUIRED NUMBER OF GROUPS PER TREATMENT COMBINATION 
    N04_p00 = 3
    N04_p25 = 3
    N04_p50 = 3
    N08_p00 = 3
    N08_p25 = 3
    N08_p50 = 3


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
    scenarios = list(C.SCENARIOS['code'])
    scenario_counts = {}
    for i_sce, sce in enumerate(scenarios):
        scenario_counts[sce] = {}
        scenario_counts[sce]['A'] = []
        scenario_counts[sce]['F'] = []

    for p in waiting_players:
        for i_sce, sce in enumerate(scenarios):
            if sce in response[p.participant.code].keys():
                if response[p.participant.code][sce] == -1:
                    scenario_counts[sce]['A'].append(p)
                elif response[p.participant.code][sce] == 1:
                    scenario_counts[sce]['F'].append(p)
    print(scenario_counts)

    # players waiting for more than threshold need to be let go  
    long_waiting = [p for p in waiting_players if long_wait(p)]
    if len(long_waiting) >= 1:
        for player in long_waiting:
            print('Ready to let participant go, waiting for too long')
            return [player]
            
    # check if creating 1 group of 8 is possible 
    if len(waiting_players) >= C.N_TEST: 
        print('Ready to check LARGE discussion group')
        temp_scenarios = scenarios.copy()
        temp_scenarios = random.sample(temp_scenarios, len(temp_scenarios))
        
        for i_sce, sce in enumerate(temp_scenarios):
            if len(scenario_counts[sce]['A']) == C.N_TEST/2 and len(scenario_counts[sce]['F']) == C.N_TEST/2: 
                print('Ready to create a LARGE discussion group')
                group = scenario_counts[sce]['A']+scenario_counts[sce]['F']
                for p in group:
                    p.participant.scenario = sce  # setting a scenarioi group-level variable
                return group
                break

    else: 
        print('not enough players yet to create a group')
        # players waiting for medium time, check if smaller group possible 
        medium_waiting = [p for p in waiting_players if medium_wait(p)]
        if len(medium_waiting) >= C.N_TEST/2:
            print('Ready to check SMALL discussion group')
            temp_scenarios = scenarios.copy()
            temp_scenarios = random.sample(temp_scenarios, len(temp_scenarios))
            
            for i_sce, sce in enumerate(temp_scenarios):
                if len(scenario_counts[sce]['A']) == C.N_TEST/2:
                    group = scenario_counts[sce]['A']
                elif len(scenario_counts[sce]['F']) == C.N_TEST/2:
                    group = scenario_counts[sce]['F']
                else:
                    continue  # if neither condition is met, skip to the next 'sce'

                for p in group:
                    p.participant.scenario = sce
                return group  # only runs if 'group' was set
                break


class Group(BaseGroup):
    group_size = models.StringField(initial='single')
    is_group_single = models.BooleanField()
    beta_50 = models.BooleanField()  # for beta 0.50 treatment
    anti_prop = models.StringField()  # for p value treatment

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

def p_00(group:Group):
    group.anti_prop = 'p00'

def p_25(group:Group):
    group.anti_prop = 'p25'

def p_50(group:Group):
    group.anti_prop = 'p50'

def random_p(group:Group):
    group.anti_prop = random.choice(['p00','p25','p50'])


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
        
        if len(group_players) == C.N_TEST:
            group_size = 'N08'
            is_group_single = False
        elif len(group_players) == C.N_TEST/2:
            group_size = 'N04'
            is_group_single = False
        else:
            group_size = 'single'
            is_group_single = True     

        # Save to the group model (for round 1 only)
        group.group_size = group_size
        group.is_group_single = is_group_single 

        if not group.is_group_single:
            if group.group_size == 'N08':
                group.beta_50 = True
                conditions = [
                    (session.N08_p00 < C.N08_p00, p_00),
                    (session.N08_p25 < C.N08_p25, p_25),
                    (session.N08_p50 < C.N08_p50, p_50)]              
            elif group.group_size == 'N04':
                group.beta_50 = False
                conditions = [
                    (session.N04_p00 < C.N04_p00, p_00),
                    (session.N04_p25 < C.N04_p25, p_25),
                    (session.N04_p50 < C.N04_p50, p_50)] 
                
            # Shuffle the order
            random.shuffle(conditions)
            # Evaluate conditions
            for condition, action in conditions:
                if condition:
                    action(group)
                    break
            else:
                print("Condition: fallback (random choice)")
                # if all quotas are full, choose randomly
                random_p(group)

        # Save persistently to participant
        # REVIEW 
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

        if group.subsession.round_number == 1:
            # Define how many anticonformists in each faction based on group parameter
            if group.anti_prop == 'p50':
                n_anti = 2
            elif group.anti_prop == 'p25':
                n_anti = 1
            # Select participants to be anticonformists 
            if group.group_size == 'N08':
                faction_A = [p.participant.code for p in group.get_players() if p.participant.all_responses[p.participant.scenario]==-1]
                faction_F = [p.participant.code  for p in group.get_players() if p.participant.all_responses[p.participant.scenario]==1]
                anticonformists = random.sample(faction_A,n_anti) + random.sample(faction_F,n_anti) 
            elif group.group_size == 'N04':
                faction_U = group.get_players() 
                anticonformists = random.sample(faction_U,n_anti)
            else:
                anticonformists = []
            # Assign anticonformists to their participant level variable
            for player in group.get_players():
                if player.participant.code in anticonformists:
                    player.participant.anticonformist = True 

            for player in group.get_players():
                scenario_position = player.participant.all_responses[player.participant.scenario]
                if scenario_position==-1:
                    player.participant.own_faction = [p.participant.code for p in group.get_players() if p.participant.all_responses[p.participant.scenario]==-1]
                    player.participant.other_faction = [p.participant.code for p in group.get_players() if p.participant.all_responses[p.participant.scenario]==1]

                elif scenario_position==1:
                    player.participant.own_faction = [p.participant.code for p in group.get_players() if p.participant.all_responses[p.participant.scenario]==1]
                    player.participant.other_faction = [p.participant.code for p in group.get_players() if p.participant.all_responses[p.participant.scenario]==-1] 
                
                else:
                    player.participant.own_faction = []
                    player.participant.other_faction = []

        else:
            # Copy group variable settings from round 1
            group.group_size = group.in_round(1).group_size
            group.is_group_single = group.in_round(1).is_group_single 
            group.beta_50 = group.in_round(1).beta_50
            group.anti_prop = group.in_round(1).anti_prop  

        if group.subsession.round_number == 1:
            for p in group.get_players():
                p.old_response = p.participant.all_responses[p.participant.scenario]
        else:
            for p in group.get_players():
                p.old_response = p.in_round(p.round_number - 1).new_response

        if group.group_size == 'N08':
            for p in group.get_players():
                factions = [random.choice(['own','other']) for i in range((C.N_TEST/2)-1)]
                labels, counts = np.unique(factions, return_counts=True)
                # Convert to plain str and int types
                faction_counts = {str(label): int(count) for label, count in zip(labels, counts)}
                faction_map = {
                    'own': player.participant.own_faction,
                    'other': player.participant.other_faction,
                    # Add more if needed
                }
                discussion_temp = []
                for key in faction_counts.keys():
                    discussion_temp = discussion_temp + random.sample(faction_map[key],faction_counts[key])
                p.discussion_grp = str(discussion_temp)
                p.participant.discussion_grp = [o for o in p.get_others_in_group() if o.participant.code in discussion_temp]

        if group.group_size == 'N04':
            for p in group.get_players():
                others = p.get_others_in_group()
                p.participant.discussion_grp = others
                p.discussion_grp = str([o.participant.code for o in others])

        for other in p.participant.discussion_grp:
            print(other.id_in_group,other.old_response)

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


page_sequence = [GroupingWaitPage, GroupSizeWaitPage, DiscussionGRPWaitPage]
# page_sequence = [GroupingWaitPage, GroupSizeWaitPage, DiscussionGRPWaitPage, Phase3, Nudge, Discussion]
