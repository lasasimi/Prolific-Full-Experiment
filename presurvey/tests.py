# myapp/tests.py

from otree.api import Bot
from . import * 

class PlayerBot(Bot):
    def play_round(self):
        if self.player.round_number == 1:
            yield Introduction, dict(
                gives_consent=True)
            if self.player.id_in_group in range(1,5):
                yield Demographics, dict(
                age=34,
                gender="Woman",
                education_lvl='Less than high school', 
                neighborhood_type='Urban',
                political_affiliation='Democrat')
            elif self.player.id_in_group in range(5, 9):
                yield Demographics, dict(
                age=34,
                gender="Woman",
                education_lvl='Less than high school', 
                neighborhood_type='Urban',
                political_affiliation='Republican')
            yield NeighborhoodInstruction
            # This is because the submit button is not a default submit button
            yield Submission(Training, 
                            {'test_scenario': '-1'}, 
                            check_html=False)    
            yield TrainingNeighbor_1, dict(
                dilemmatopic=1,
                majority=1,
                howmanyneighbors=1)

            yield ExperimentInstruction
            if self.player.id_in_group in range(1,5):
                yield Scenario, dict(
                    political_charge=1,
                    emotional_charge=1,
                    response=1
                )
            elif self.player.id_in_group in range(5, 9):
                yield Scenario, dict(
                    political_charge=1,
                    emotional_charge=1,
                    response=0
                )
        else:
            yield Scenario, dict(
                political_charge=1,
                emotional_charge=1,
                response=0
            )
