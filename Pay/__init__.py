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
        return player.participant.active and not player.participant.single_group

# PAGES
class MyPage(Page):
    form_model = 'player'
    # JS vars to determine which link and reason to display based on if they finished the entire app (participant.single_group == False) or waited too long
    @staticmethod
    def js_vars(player: Player):
        if player.participant.single_group == False and player.participant.failed_commitment == True:
            player.participant.reason="You did not commit to entering the next phase of the study."
            return dict(
                pay= player.subsession.session.config['completionlink']
            )

        elif player.participant.single_group == True:
            player.participant.reason="You were the only participant in your group and we could not find you other participants to join your group. Thanks for your time!"
            return dict(
                pay= player.subsession.session.config['waitingbonuslink']
            )
        
        elif player.participant.single_group == False and player.participant.failed_commitment == False:
            player.participant.reason="Thanks for participating! Since you completed the entire study, you will receive the bonus payment."
            return dict(
                pay=player.subsession.session.config['bonuslink']
            )
        
    @staticmethod
    def is_displayed(player: Player):
        if player.participant.failed_commitment:
            return player.participant.gives_consent 
        else:
            return player.participant.active

page_sequence = [Feedback, MyPage]
