# myapp/tests.py

from otree.api import Bot, SubmissionMustFail
from . import *

class PlayerBot(Bot):
    def play_round(self):
            if self.player.round_number == 1:
                yield Submission(GroupingWaitPage, check_html=False)
                yield Submission(DiscussionGRPWaitPage, check_html=False)
                if not self.player.participant.no_nudge:
                    yield Submission(Nudge, check_html=False)
                yield Submission(Discussion, 
                            dict(response= random.choice([-1, 0, 1])),
                            check_html=False)
            else:
                yield Submission(DiscussionGRPWaitPage, check_html=False)
                yield Submission(Discussion, 
                            dict(response= random.choice([-1, 0, 1])),
                            check_html=False)
        
        

        