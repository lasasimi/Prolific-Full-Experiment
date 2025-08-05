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
        # From presurvey app
        if player.participant.failed_attention_check:
            player.participant.reason="You did not pass the attention check."
        elif player.participant.training_attempt == 0:
            player.participant.reason="You did not pass the Training phase by answering incorrectly for too many times."
        elif not player.participant.gives_consent:
            player.participant.reason="You did not consent to participate in the study."
        # From mock app
        elif not player.participant.active:
            player.participant.reason="You have been timed out for inactivity."
        return dict(
                nopay=player.subsession.session.config['returnlink'],
            )

    @staticmethod
    def is_displayed(player: Player):
        # if they did not complete presurvey, they did not get payment either because they were not active in the mock app, or did not pass the attention/training(complete_presurvey), or did not give consent
        if not player.participant.complete_presurvey:
            return not player.participant.active or not player.participant.gives_consent or player.participant.failed_attention_check or player.participant.training_attempt == 0

page_sequence = [ExitPage]
