# myapp/tests.py

from otree.api import Bot, SubmissionMustFail
from . import *

class PlayerBot(Bot):
    def play_round(self):
        if self.player.round_number == 1:
            yield Submission(GroupingWaitPage, check_html=False)
            yield Submission(DiscussionGRPWaitPage, check_html=False)
            yield Submission(Nudge, check_html=False)
            yield Submission(Discussion, 
                        dict(response= random.choice([-1, 0, 1])),
                        check_html=False)
        else:
            yield Submission(DiscussionGRPWaitPage, check_html=False)
            yield Submission(Discussion, 
                        dict(response= random.choice([-1, 0, 1])),
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
            