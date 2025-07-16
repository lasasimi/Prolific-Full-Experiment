# myapp/tests.py

from otree.api import Bot, SubmissionMustFail
from . import *

class PlayerBot(Bot):
    def play_round(self):
        if self.player.round_number == 1:
            yield Phase3
            yield Nudge
            yield Submission(Discussion, 
                        dict(new_response= random.choice([-1, 0, 1])),
                        check_html=False)
        else:
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
            