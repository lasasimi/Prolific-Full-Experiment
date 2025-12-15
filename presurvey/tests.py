# myapp/tests.py
'''
from otree.api import Bot
from . import * 

class PlayerBot(Bot):
    def play_round(self):
        # Introduction page
        yield Introduction, dict(gives_consent=True)
        
        # AudioCheck page
        yield Submission(AudioCheck, dict(
            audio_answer=4,  # correct answer: wave crashes
            audio_answer_image=5,  # correct answer
            audio_unlocked=True
        ), check_html=False)
        
        # Scenario page - assign responses based on id_in_subsession
        # Players 1-2 will be purple (For=1), players 3-4 will be green (Against=-1)
        if self.player.id_in_subsession % 2 == 1:
            response = 1  # For (purple team)
        else:
            response = -1  # Against (green team)
        
        yield Scenario, dict(
            political_charge=3,
            emotional_charge=3,
            response=response
        )
        
        # Commitment page
        yield Commitment, dict(
            commit_attention_Q1=True,
            commit_attention_Q2=True,
            commit_attention_Q3=True,
        )
'''

from otree.api import Bot, Submission
from . import *

class PlayerBot(Bot):
    def play_round(self):

        # 1) Introduction / consent
        if Introduction.is_displayed(self.player):
            yield Introduction, dict(gives_consent=True)
            
        
        # 2) AudioCheck
        if AudioCheck.is_displayed(self.player):
            # IMPORTANT: these keys MUST match AudioCheck.form_fields
            yield Submission(
                AudioCheck,
                dict(
                    audio_answer=4,        # correct option index/value
                    audio_answer_image=5,  # correct option index/value
                    audio_unlocked=True,
                ),
                check_html=False,  # ignore JS/audio-specific HTML checks
            )
        
        # 3) Scenario: give them an opinion for grouping
        if Scenario.is_displayed(self.player):
            # Example rule: odd id -> For (1), even id -> Against (-1)
            if self.player.id_in_subsession % 2 == 1:
                response = 1
            else:
                response = -1

            yield Scenario, dict(
                political_charge=3,
                emotional_charge=3,
                response=response,
            )

        # 4) Commitment page
        if Commitment.is_displayed(self.player):
            yield Commitment, dict(
                commit_attention_Q1=True,
                commit_attention_Q2=True,
                commit_attention_Q3=True,
            )
