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
    NUM_ROUNDS = 2 # NOTE: REPLACE WITH 20 FOR FULL EXPERIMENT
    LONG_WAIT = 20 #(minutes) # IF NO GROUP HAS BEEN FORMED, LET GO AND PAY WAITING BONUS
    # NOTE: Set this to 9.5 minutes
    MEDIUM_WAIT = 0.5 # (minutes) # IF NO GROUP OF 8 HAS BEEN FORMED, CREATE A GROUP OF 4
    N_TEST = 8 # SIZE OF DISCUSSION GROUP 
    MAX_FORCED = 3 #MAX NUMBER OF FORCED RESPONSES 
    
    # REMEMBER TO CHANGE TO POLITICAL/NON-POLITICAL FRAMING DEPENDING ON THE EXPERIMENTAL DESIGN
    SCENARIOS = open_CSV('presurvey/scenarios_1np.csv')
    SCE = 's2_n'
    # NOTE: Max number of groups in each condition is set up in session config

 

class Subsession(BaseSubsession):
    pass

def creating_session(subsession):
    session = subsession.session
    # Retrieve values from session config and store them in the session
    session.MAX_N04_p00 = session.config.get('N04_p00', 0)
    session.MAX_N04_p25 = session.config.get('N04_p25', 0)
    session.MAX_N04_p50 = session.config.get('N04_p50', 0)
    session.MAX_N08_p00 = session.config.get('N08_p00', 0)
    session.MAX_N08_p25 = session.config.get('N08_p25', 0)
    session.MAX_N08_p50 = session.config.get('N08_p50', 0)

def N08_full(subsession):
    session = subsession.session
    return (
    session.N08_p00 == session.MAX_N08_p00 and
    session.N08_p25 == session.MAX_N08_p25 and
    session.N08_p50 == session.MAX_N08_p50
)

def long_wait(player):
    participant = player.participant
    return time.time() - participant.wait_page_arrival > C.LONG_WAIT * 60  # in mins

def medium_wait(player):
    participant = player.participant
    return time.time() - participant.wait_page_arrival > C.MEDIUM_WAIT * 60  # in mins

def counters_full(player):
    session = player.subsession.session
    return (session.N04_p00 == session.MAX_N04_p00 and session.N04_p25 == session.MAX_N04_p25 and session.N04_p50 == session.MAX_N04_p50 and
            session.N08_p00 == session.MAX_N08_p00 and session.N08_p25 == session.MAX_N08_p25 and session.N08_p50 == session.MAX_N08_p50)

def group_by_arrival_time_method(subsession, waiting_players):
    session = subsession.session
    print(f'Waiting players: {waiting_players}')
    response = {}
    for p in waiting_players:
        response[p.participant.code] = p.participant.all_responses
        p.participant.scenario = C.SCE
    
    # Getting list of scenarios, always get first key, instead of relying on p.id_in_group == 1
    #scenarios = list(C.SCENARIOS['code'])
    
    # Dynamically reconstruct scenario_counts from participant.vars
    sce = C.SCE
    scenario_counts = {sce: {'A': [], 'F': []}}
    for p in waiting_players:
        if sce in response[p.participant.code].keys():
            if response[p.participant.code][sce] == -1:
                scenario_counts[sce]['A'].append(p)
            elif response[p.participant.code][sce] == 1:
                scenario_counts[sce]['F'].append(p)
    print(f"Debug: Scenario counts before grouping: {scenario_counts}")

    # Check if counters are full
    if all(counters_full(p) for p in waiting_players):
        print("All counters are full. Adding all waiting players to long_waiting.")
        long_waiting = waiting_players  # Add all players to long_waiting
    else:
        # players waiting for more than threshold need to be let go
        long_waiting = [p for p in waiting_players if long_wait(p) or counters_full(p)]

    if len(long_waiting) >= 1:
        for player in long_waiting:
            print('Ready to let participant go, waiting for too long')
            return [player]

    group = []

    if len(waiting_players) == C.N_TEST and not N08_full(subsession):
    # check if creating 1 group of 8 is possible 
        print('N08 is not full, creating a group of 8')
        sce = C.SCE
        #temp_scenarios = scenarios.copy()
        #temp_scenarios = random.sample(temp_scenarios, len(temp_scenarios))
        #for i_sce, sce in enumerate(temp_scenarios):
        print(f"Debug: Scenario {sce}, A count: {len(scenario_counts[sce]['A'])}, F count: {len(scenario_counts[sce]['F'])}")
        if len(scenario_counts[sce]['A']) == C.N_TEST/2 and len(scenario_counts[sce]['F']) == C.N_TEST/2: 
            print('Ready to create a LARGE discussion group')
            group = scenario_counts[sce]['A'] + scenario_counts[sce]['F'] 
            for p in group:
                p.participant.scenario = sce
                # Save the scenario and faction to participant.vars
                p.participant.vars['scenario'] = sce
                p.participant.vars['faction'] = 'A' if p in scenario_counts[sce]['A'] else 'F'
            return group 
    # If N08 is full or any of the players has been waiting for medium time, create a group of 4
    if N08_full(subsession) or any(medium_wait(p) for p in waiting_players):
        print('N08 is full or medium wait, checking for smaller groups')
        sce = C.SCE
        if len(waiting_players) == C.N_TEST/2:
            print('Creating a group of 4')
            print(len(scenario_counts[sce]['A']), len(scenario_counts[sce]['F']))

            if len(scenario_counts[sce]['A']) >= C.N_TEST//2:
                group = scenario_counts[sce]['A']
            elif len(scenario_counts[sce]['F']) >= C.N_TEST//2:
                group = scenario_counts[sce]['F']
            
                print("About to assign scenarios to group:", group)
                for p in group:
                    p.participant.scenario = sce
                    # Save the scenario and faction to participant.vars
                    p.participant.vars['scenario'] = sce
                    p.participant.vars['faction'] = 'A' if p in scenario_counts[sce]['A'] else 'F'
                return group

    if not group:
        print('Not enough players yet to create a group')
        return []
    
    return group


class Group(BaseGroup):
    group_size = models.StringField(initial='single')
    is_group_single = models.BooleanField()
    beta_50 = models.BooleanField()  # for beta 0.50 treatment
    anti_prop = models.StringField()  # for p value treatment
    group_responses = models.LongStringField()  # store as string and later to dump as JSON
    majority_response = models.IntegerField() # to store the majority response in the final round

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
    nudge_training =  models.IntegerField(label="If you follow the tip you just read, what would be your choice?",
                                          choices=[[-1, 'Against'],
                                                   [0, 'Neutral'],
                                                   [1, 'For']],
                                                   widget=widgets.RadioSelectHorizontal())
    nudge_training_text = models.StringField() # to show what they selected
    correct_nudge_training = models.IntegerField()
    old_response_text = models.StringField() # to show previous response in the popup

def counters_update(group:Group):
    if group.group_size == 'N08':
        if group.anti_prop == 'p00':
            group.subsession.session.N08_p00 += 1
        if group.anti_prop == 'p25':
            group.subsession.session.N08_p25 += 1
        if group.anti_prop == 'p50':
            group.subsession.session.N08_p50 += 1
    if group.group_size == 'N04':
        if group.anti_prop == 'p00':
            group.subsession.session.N04_p00 += 1
        if group.anti_prop == 'p25':
            group.subsession.session.N04_p25 += 1
        if group.anti_prop == 'p50':
            group.subsession.session.N04_p50 += 1

def p_00(group:Group):
    group.anti_prop = 'p00'
    counters_update(group)

def p_25(group:Group):
    group.anti_prop = 'p25'
    counters_update(group)

def p_50(group:Group):
    group.anti_prop = 'p50'
    counters_update(group)

def random_p(group:Group):
    group.anti_prop = random.choice(['p00','p25','p50'])
    counters_update(group)


# PAGES
class GroupingWaitPage(WaitPage):
    template_name = 'mock/GroupingWaitPage.html'
    group_by_arrival_time = True
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.complete_presurvey 


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
                    (session.N08_p00 < session.MAX_N08_p00, p_00),
                    (session.N08_p25 < session.MAX_N08_p25, p_25),
                    (session.N08_p50 < session.MAX_N08_p50, p_50)]              
            elif group.group_size == 'N04':
                group.beta_50 = False
                conditions = [
                    (session.N04_p00 < session.MAX_N04_p00, p_00),
                    (session.N04_p25 < session.MAX_N04_p25, p_25),
                    (session.N04_p50 < session.MAX_N04_p50, p_50)] 
                
            # Shuffle the order
            random.shuffle(conditions)
            # Evaluate conditions
            for condition, action in conditions:
                if condition:
                    action(group)
                    print(f'Condition: non-fallback (random choice)', f'Group beta .50?:{group.beta_50}', f'Group AC prop:{group.anti_prop}')
                    break
            else: 
                # The else is not tied to the if. It runs only if none of the conditions were True, because only then does the for loop finish without breaking.

                # if all quotas are full, choose randomly
                random_p(group)
                print("Condition: fallback (random choice)", f'Group beta .50?:{group.beta_50}', f'Group AC prop:{group.anti_prop}')

        # Save persistently to participant
        # REVIEW 
        for p in group_players:
            p.participant.group_size = group_size
            p.participant.is_group_single = is_group_single
            if group_size == 'single':
                p.participant.single_group = True  # they go to the pay up, but no bonus payment 

        print(f'Debug counter: session.N04_p00:{session.N04_p00}, session.N04_p25:{session.N04_p25}, session.N04_p50:{session.N04_p50}, session.N08_p00:{session.N08_p00}, session.N08_p25:{session.N08_p25}, session.N08_p50:{session.N08_p50}')
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.complete_presurvey


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
            else:
                n_anti = 0
            print(f"Debug: n_anti = {n_anti}, group.anti_prop = {group.anti_prop}")
            # Select participants to be anticonformists 
            if group.group_size == 'N08':
                faction_A = [p.participant.code for p in group.get_players() if p.participant.all_responses[p.participant.scenario]==-1]
                faction_F = [p.participant.code  for p in group.get_players() if p.participant.all_responses[p.participant.scenario]==1]
                anticonformists = random.sample(faction_A,n_anti) + random.sample(faction_F,n_anti) 
                print(f"Debug: anticonformists = {anticonformists}")

                # Extract participant codes from the anticonformists list
                anticonformists_codes = anticonformists
                print(f"Debug: anticonformists codes = {anticonformists}")

            elif group.group_size == 'N04':
                faction_U = group.get_players() 
                anticonformists = random.sample(faction_U,n_anti)
                print(f"Debug: anticonformists = {anticonformists}")

                # Extract participant codes from the anticonformists list
                anticonformists_codes = [p.participant.code for p in anticonformists]
                print(f"Debug: anticonformists codes = {anticonformists_codes}")
            else:
                anticonformists = []
            # Assign anticonformists to their participant level variable
            for player in group.get_players():
                if player.participant.code in anticonformists_codes:
                    player.participant.anticonformist = True 

            for player in group.get_players():
                scenario_position = player.participant.all_responses[player.participant.scenario]
                if scenario_position==-1:
                    player.participant.own_faction = [other.participant.code for other in player.get_others_in_group() if other.participant.all_responses[other.participant.scenario]==-1]
                    player.participant.other_faction = [other.participant.code for other in player.get_others_in_group() if other.participant.all_responses[other.participant.scenario]==1]

                elif scenario_position==1:
                    player.participant.own_faction = [other.participant.code for other in player.get_others_in_group() if other.participant.all_responses[other.participant.scenario]==1]
                    player.participant.other_faction = [other.participant.code for other in player.get_others_in_group() if other.participant.all_responses[other.participant.scenario]==-1] 
                
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
                factions = [random.choice(['own','other']) for i in range(int(C.N_TEST/2)-1)]
                labels, counts = np.unique(factions, return_counts=True)
                # Convert to plain str and int types
                faction_counts = {str(label): int(count) for label, count in zip(labels, counts)}
                faction_map = {
                    'own': p.participant.own_faction,
                    'other': p.participant.other_faction,
                    # Add more if needed
                }
                
                print(f"Debug: faction map {faction_map}, faction counts {faction_counts}")
                p.participant.discussion_grp = []
                for key in faction_counts.keys():
                    p.participant.discussion_grp = p.participant.discussion_grp + random.sample(faction_map[key],faction_counts[key])
                p.discussion_grp = str(p.participant.discussion_grp)

        if group.group_size == 'N04':
            for p in group.get_players():
                others = p.get_others_in_group()
                p.participant.discussion_grp = [o.participant.code for o in others]
                p.discussion_grp = str(p.participant.discussion_grp)

        for player in group.get_players():
            print(f"Debug: player's discussion group: {player.participant.discussion_grp}")

    @staticmethod
    def is_displayed(player):
        return player.participant.complete_presurvey and not player.participant.single_group


class Phase3(Page):
    timeout_seconds =  3600
    #timeout_seconds = 45 # to force proceed after 45 seconds of inactivity
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.complete_presurvey and not player.participant.single_group    


class Nudge(Page):
    timeout_seconds = 90 # to force proceed after 45 seconds of inactivity
    #timeout_seconds = 3600
    form_model = 'player'
    form_fields = ['nudge_training']

    @staticmethod
    def vars_for_template(player: Player):
        row = C.SCENARIOS[C.SCENARIOS['code']==player.participant.scenario]

        return dict(
            scenario_against = 'option A',
            scenario_neutral = 'option B',
            scenario_for ='option C',
            # Some made up responses of other players' to be displayed
            others_responses = [1, -1, 1],# anticonformist should answer 0, conformist should answer 1
            anticonformist = player.participant.anticonformist, # treatment variable
        )
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened: # choose the wrong answers randomly
            if player.participant.anticonformist:
                player.nudge_training = random.choice([-1, 1])
            else:
                player.nudge_training = random.choice([-1, 0])

        player.participant.nudge_training = player.nudge_training
        

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.complete_presurvey and not player.participant.single_group

class NudgeTraining(Page):
    form_model = 'player'
    form_fields = []
    #timeout_seconds = 3600
    timeout_seconds = 3600
    
    @staticmethod
    def vars_for_template(player):
        if player.participant.anticonformist:
            player.correct_nudge_training = 0
        else:
            player.correct_nudge_training = 1
        
        if player.participant.nudge_training == player.correct_nudge_training:
            player.participant.correct_nudge_training = True
        else:
            player.participant.correct_nudge_training = False


        row = C.SCENARIOS[C.SCENARIOS['code']==player.participant.scenario]

        if player.participant.nudge_training == 1:
            player.nudge_training_text = 'option C'
        elif player.participant.nudge_training == 0:
            player.nudge_training_text = 'option B'
        else:
            player.nudge_training_text = 'option A'

        return dict(
            correct_nudge_training = player.participant.correct_nudge_training,
            nudge_training_text = player.nudge_training_text,
            anticonformist = player.participant.anticonformist,
            others_responses = [1, -1, 1],
            scenario_against = 'option A',
            scenario_neutral = 'option B',
            scenario_for = 'option C',
        )
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.participant.complete_presurvey and not player.participant.single_group  



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
        print(f'Scenario code in the discussion: {player.participant.scenario}')
        #print(C.SCENARIOS)
        row = C.SCENARIOS[C.SCENARIOS['code']==player.participant.scenario]

        discussion_partners = [other for other in player.get_others_in_group() if other.participant.code in player.participant.discussion_grp]   
        
        # Store the text of their previous response for the popup
        if player.old_response == 1:
            player.old_response_text = row.iloc[0]['For']
        elif player.old_response == 0:
            player.old_response_text = row.iloc[0]['Neutral']
        else:  
            player.old_response_text = row.iloc[0]['Against']

        return dict(
            scenario_title = row.iloc[0]['Title'],
            scenario_text = row.iloc[0]['Text'],
            scenario_against = row.iloc[0]['Against'],
            scenario_neutral = row.iloc[0]['Neutral'],
            scenario_for = row.iloc[0]['For'],
            others_responses = [other.old_response for other in discussion_partners if other.id_in_group != player.id_in_group],
            anticonformist = player.participant.anticonformist,
            old_response_text = player.old_response_text,
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            ### TODO: REVIEW THE RULE #### 
            player.forced_response = True # only in the last round, make them inactive
            player.new_response = random.choice([-1, 0, 1])
            
            player.participant.forced_response_counter += 1
            if player.participant.forced_response_counter > C.MAX_FORCED:
                player.participant.active = False 
        if player.round_number == C.NUM_ROUNDS and not player.participant.active:
            player.participant.complete_presurvey = False

    @staticmethod
    def is_displayed(player):
        print(f"Debug: Bot is {player.participant.code}, on round {player.round_number}")
        return player.participant.complete_presurvey and not player.participant.single_group

class FinalRoundWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        # This code runs once for each group, after all players in the group reach the wait page
        group_responses = [p.new_response for p in group.get_players()]
        counts = {}
        for r in group_responses:
            counts[r] = counts.get(r, 0) + 1

        # save as JSON string
        group.group_responses = json.dumps(group_responses)

        max_count = max(counts.values())
        majority_responses = [val for val, cnt in counts.items() if cnt == max_count]
        if len(majority_responses) == 1:
            group.majority_response = majority_responses[0] 
        else:
            group.majority_response = 99 # Tie / No majority

    @staticmethod
    def is_displayed(player:Player):
        return player.round_number == C.NUM_ROUNDS and player.participant.complete_presurvey and not player.participant.single_group
    
class FinalRound(Page):
    @staticmethod
    def vars_for_template(player: Player):
        # Get scenario details
        row = C.SCENARIOS[C.SCENARIOS['code']==player.participant.scenario]
        group = player.group
        group_responses = json.loads(group.group_responses)
    
        return dict(
            group_responses= group_responses,
            majority_response= group.majority_response,
            scenario_against = row.iloc[0]['Against'],
            scenario_neutral = row.iloc[0]['Neutral'],
            scenario_for = row.iloc[0]['For']
        )
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS and player.participant.complete_presurvey and not player.participant.single_group

page_sequence = [GroupingWaitPage, GroupSizeWaitPage, DiscussionGRPWaitPage, Nudge, NudgeTraining, Phase3, Discussion, FinalRoundWaitPage, FinalRound]
