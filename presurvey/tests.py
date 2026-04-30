# myapp/tests.py

from otree.api import Bot
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
                    audio_unlocked=True,
                    audio_answer=4,        # correct option index/value
                    audio_answer_image=5,  # correct option index/value
                ),
                check_html=False,  # ignore JS/audio-specific HTML checks
            )
        if Demographics.is_displayed(self.player):
            yield Demographics, dict(
            age=34,
            gender="Woman",
            education_lvl='Less than high school', 
            neighborhood_type='Urban',
            political_affiliation=1)
        
        if NeighborhoodInstruction.is_displayed(self.player):
            yield NeighborhoodInstruction
        # This is because the submit button is not a default submit button
        if Training.is_displayed(self.player):
            yield Submission(Training, 
                            {'test_scenario': '-1'}, 
                            check_html=False)    
        if TrainingNeighbor_1.is_displayed(self.player):
            yield TrainingNeighbor_1, dict(
                dilemmatopic=1,
                majority=1,
                howmanyneighbors=1)

        if ExperimentInstruction.is_displayed(self.player):
            yield ExperimentInstruction

        if Scenario.is_displayed(self.player):
            block_size = 5

            # which block the participant belongs to
            block_index = (self.player.id_in_group - 1) // block_size

            # alternate between 1 and -1, first block answers 1, second block answers -1, etc.
            response = 1 if block_index % 2 == 0 else -1

            yield Scenario, dict(
                political_charge=1,
                emotional_charge=1,
                response=response,
            )
        
        if Commitment.is_displayed(self.player):
            yield Commitment, dict(
                commit_attention_Q1=True,
                commit_attention_Q2=True,
                commit_attention_Q3=True,
            )
