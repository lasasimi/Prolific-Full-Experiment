from otree.api import *
import numpy as np # type: ignore
import json
import time
import random


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'mock'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1
    SCENARIOS = ['s13_p','s3_n','s11_p']


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
        if p.id_in_group == 1:
            scenarios = [key for key in p.participant.all_responses]
        
        response[p.participant.code] = p.participant.all_responses

    scenario_counts = {}
    for i_sce, sce in enumerate(scenarios):
        scenario_counts[sce] = {}
        scenario_counts[sce]['A'] = []
        scenario_counts[sce]['F'] = []

    for p in waiting_players:
        # print(p.id_in_group)
        for i_sce, sce in enumerate(scenarios):
            try:
                if response[p.participant.code][sce] == -1:
                    scenario_counts[sce]['A'].append(p)
                else:
                    scenario_counts[sce]['F'].append(p)
            except:
                pass
    
    # players waiting for more than 10 mins 
    long_waiting = [p for p in waiting_players if long_wait(p)]
    if len(long_waiting) > 1:
            for player in long_waiting:
                print('Ready to let participant go, waiting for too long')
                return [player]
                break
    
    ##### BLOCK 0 #####
    if len(waiting_players) > 5: ##### TEST ONLY!! CHANGE LATER to 20/6 #####
        print('Ready to check discussion group')
        temp_scenarios = scenarios.copy()
        temp_scenarios = random.sample(temp_scenarios, len(temp_scenarios))
        # players waiting for more than 5 mins are considered of medium wait
        medium_waiting = [p for p in waiting_players if medium_wait(p)]
        
        ##### BLOCK 1 #####
        for i_sce, sce in enumerate(temp_scenarios):
            if len(scenario_counts[sce]['A']) == 3 and len(scenario_counts[sce]['F']) == 3: ##### TEST ONLY!! CHANGE LATER to CORRECT 50/50#####
                print('Ready to create a 50/50 group N=6')
                print(sce,scenario_counts[sce]['A']+scenario_counts[sce]['F'])
                return(scenario_counts[sce]['A']+scenario_counts[sce]['F'])
                break

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

    else: 
        print('not enough players yet to create a group')


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class GroupingWaitPage(WaitPage):
    #print(C.RESPONSES)
    print(C.SCENARIOS)
    group_by_arrival_time = True


class MyPage(Page):

    @staticmethod
    def vars_for_template(player: Player):
        # Access the variables from the previous app
        combined_responses = player.session.vars['combined_responses']
        print(player.participant.wait_page_arrival)
        return dict(
            combined_responses=combined_responses
        )
    
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.gives_consent and player.participant.active == "active"
          

class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [GroupingWaitPage]
