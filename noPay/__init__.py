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

    @staticmethod
    def js_vars(player):
        return dict(
            didnotconsent = player.subsession.session.config['returnlink']
        )

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.gives_consent or player.participant.active == "inactive"


page_sequence = [ExitPage]
