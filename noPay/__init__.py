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
            return dict(
                nopay=player.subsession.session.config['returnlink'],
            )
        elif player.participant.active == False:
            player.participant.reason="You did not consent to participate in the study or or timed out for inactivity."
            return dict(
                nopay=player.subsession.session.config['returnlink'],
            )

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.gives_consent or not player.participant.active


page_sequence = [ExitPage]
