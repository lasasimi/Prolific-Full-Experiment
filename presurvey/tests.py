# myapp/tests.py

from otree.api import Bot
from . import * 

class PlayerBot(Bot):
    def play_round(self):
        # Introduction page
        yield Introduction, dict(gives_consent=True)
        
        # AudioCheck page
        yield AudioCheck, dict(
            audio_answer=4,  # correct answer: wave crashes
            audio_answer_image=5,  # correct answer
            audio_unlocked=True
        )
        
        # Scenario page - assign responses based on id_in_subsession
        # Players 1-2 will be purple (For=1), players 3-4 will be green (Against=-1)
        if self.player.id_in_subsession in [1, 2]:
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
