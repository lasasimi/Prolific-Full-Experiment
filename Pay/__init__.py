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
    pass


# PAGES
class MyPage(Page):
    # For not consenting participants
    form_model = 'player'

    @staticmethod
    def js_vars(player):
        return dict(
            completionlink = player.subsession.session.config['completionlink']
        )

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.gives_consent or player.participant.active == True



page_sequence = [MyPage]
