from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'noPay'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class ExitPage(Page):
    # For not consenting participants
    form_model = 'player'

    # Conditional JS variables based on participant status, same links but different reasons
    @staticmethod
    def js_vars(player: Player):
        if player.participant.failed_attention_check:
            player.participant.reason="You did not pass the attention check."
        elif player.participant.training_attempt == 0:
            player.participant.reason="You did not pass the Training phase by answering incorrectly for too many times."
        elif player.participant.active == False:
            player.participant.reason="You did not consent to participate in the study or or timed out for inactivity."
        
        return dict(
                nopay=player.subsession.session.config['returnlink'],
            )

    @staticmethod
    def is_displayed(player: Player):
        if not player.participant.failed_commitment:
            return not player.participant.gives_consent or not player.participant.active 

page_sequence = [ExitPage]
