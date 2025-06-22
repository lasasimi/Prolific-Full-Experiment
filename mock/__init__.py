from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'mock'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES


class MyPage(Page):
    pass
""" 
    @staticmethod
    def vars_for_template(player: Player):
        # Access the variables from the previous app
        combined_responses = player.session.vars['combined_responses']
        print(player.participant.wait_page_arrival)
        return dict(
            combined_responses=combined_responses
        )
 """       
    
    
        

class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MyPage]
