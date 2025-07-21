from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'Pay'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    feedback_final = models.LongStringField(label="Please provide your feedback here:",
                                            blank=True)


class Feedback(Page):
    form_model = 'player'
    form_fields = ['feedback_final']
    
    @staticmethod
    def is_displayed(player:Player):
        return player.participant.complete_presurvey and player.participant.active

    @staticmethod
    def js_vars(player: Player):
       return dict(pay=player.subsession.session.config['completelink'])
       
# PAGES
class MyPage(Page):
    form_model = 'player'
    # JS vars to determine which link and reason to display based on if they finished the entire app (participant.single_group == False) or waited too long
    @staticmethod
    def js_vars(player: Player):
        # completed the entire study
        player.participant.reason="Thanks for participating! Since you completed the entire study, you will receive the bonus payment."
        return dict(
            pay=player.subsession.session.config['completelink']
        )
        
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.complete_presurvey and player.participant.active
        
page_sequence = [Feedback, MyPage]
