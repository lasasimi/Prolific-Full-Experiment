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
        return player.participant.complete_presurvey and not player.participant.single_group

    @staticmethod
    def js_vars(player: Player):
       return dict(pay=player.subsession.session.config['bonuslink'])
       
# PAGES
class MyPage(Page):
    form_model = 'player'
    # JS vars to determine which link and reason to display based on if they finished the entire app (participant.single_group == False) or waited too long
    @staticmethod
    def js_vars(player: Player):
        # completed the presurvey, but were not eligible (answered neutral in all questions)
        if not player.participant.eligible_notneutral:
            player.participant.reason="Sorry, we could not find you eligible for the next phase of the study. You will still receive your base payment. Thanks for your time!"
            return dict(
                pay=player.subsession.session.config['basepaylink']
            )
        # completed the presurvey, but did not commit
        elif player.participant.failed_commitment == True:
            player.participant.reason="You did not commit to entering the next phase of the study. You will still receive your base payment. Thanks for your time!"
            return dict(
                pay=player.subsession.session.config['basepaylink']
            )
        # completed the presurvey, but did not complete the mock app
        elif player.participant.single_group == True:
            player.participant.reason="You were the only participant in your group and we could not find you other participants to join your group. Thanks for your time!"
            return dict(
                pay=player.subsession.session.config['bonuslink']
            )
        # completed the mock app
        elif player.participant.single_group == False:
            player.participant.reason="Thanks for participating! Since you completed the entire study, you will receive the bonus payment."
            return dict(
                pay=player.subsession.session.config['bonuslink']
            )
        
    @staticmethod
    def is_displayed(player: Player):
        # if they were not eligible, we need to check if they were active and did not fail the attention check
        if not player.participant.eligible_notneutral: # those who were not eligible
            return player.participant.active and not player.participant.failed_attention_check 
        else:
            return not player.participant.failed_attention_check and (player.participant.single_group or player.participant.active)
        
page_sequence = [Feedback, MyPage]
