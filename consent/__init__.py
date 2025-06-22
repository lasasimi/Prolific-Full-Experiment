from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'consent'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


def creating_session(subsession):
    for player in subsession.get_players():
        # Shuffle the scenario order for each player
        player.participant.vars['no_consent'] = False # Initialize no consent variable


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Consent variables
    gives_consent = models.BooleanField(
        label="I acknowledge that I have read and understood the information above "
        "and confirm that I wish to participate in this study.")


# PAGES
class Introduction(Page):
    form_model = 'player'
    form_fields = ['gives_consent']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        
        player.participant.gives_consent = player.gives_consent
        if player.gives_consent:
            player.participant.vars['no_consent'] = False
        else:
            player.participant.vars['no_consent'] = True
        
        print("CONSENT:", player.gives_consent,player.participant.vars['no_consent'])


page_sequence = [Introduction]
