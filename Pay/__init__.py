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
    form_model = 'player'
    # JS vars to determine which link and reason to display based on if they finished the entire app (participant.single_group == False) or waited too long
    @staticmethod
    def js_vars(player: Player):
        if player.participant.single_group == False:
            player.participant.reason="Thanks for participating! Since you completed the entire study, you will receive the bonus payment."
            return dict(
                completionlink=player.subsession.session.config['completionlink']
            )
        elif player.participant.single_group == True:  
            player.participant.reason="You were the only participant in your group and we could not find you other participants to join your group. Thanks for your time!"
            return dict(
                completionlink= player.subsession.session.config['nobonuslink']
            )

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.active or not player.participant.single_group



page_sequence = [MyPage]
