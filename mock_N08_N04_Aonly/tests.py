# myapp/tests.py

from otree.api import Bot, SubmissionMustFail
from . import *

class PlayerBot(Bot):
    def play_round(self):
        if not self.player.participant.single_group:    
            if self.player.round_number == 1:
                self.player.participant.wait_page_arrival = time.time() - (1 * 60 + 5)
                if Nudge.is_displayed(self.player):
                    yield Submission(Nudge,
                                    dict(nudge_training=1,),
                                    check_html=False)
                if NudgeTraining.is_displayed(self.player):
                    yield Submission(NudgeTraining,
                                    dict(nudge_training_two=1,),
                                    check_html=False) 
                if NudgeTrainingLast.is_displayed(self.player):
                    yield Submission(NudgeTrainingLast,
                                    dict(nudge_training_three=1,),
                                    check_html=False)

                if Phase3.is_displayed(self.player):
                    yield Phase3
                
                if Discussion.is_displayed(self.player):
                    yield Submission(Discussion, 
                                    dict(new_response= random.choice([-1, 0, 1])),
                                    check_html=False)
            elif self.player.round_number == C.NUM_ROUNDS:
                if Discussion.is_displayed(self.player):
                    yield Submission(Discussion, 
                        dict(new_response= random.choice([-1, 0, 1])),
                        check_html=False)
                if FinalRound.is_displayed(self.player):
                    yield FinalRound 
            else:
                if Discussion.is_displayed(self.player):
                    yield Submission(Discussion, 
                                dict(new_response= random.choice([-1, 0, 1])),
                                check_html=False)
                    

            # if self.player.round_number == 1:
            #     yield Discussion, dict(
            #         new_response = -1)
            # elif self.player.round_number == 2:
            #     yield Discussion, dict(
            #         new_response = 0)
            # else:
            #     yield Discussion, dict(
            #         new_response = 1)
        else:
            if self.player.round_number == 1:
                if AttentionCheck.is_displayed(self.player):
                    yield Submission(AttentionCheck,
                                    dict(attention_check=True),
                                    check_html=False)        