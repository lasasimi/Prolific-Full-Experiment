# myapp/tests.py

from otree.api import Bot, SubmissionMustFail
from . import *

class PlayerBot(Bot):
    def play_round(self):
        if self.player.participant.single_group:
            yield Submission(Feedback, 
                    dict(feedback_final='This is a test feedback.',
                        future_participation=True), 
                    check_html=False)
            yield Submission(MyPage, 
                    check_html=False)
        else:
            yield Submission(Feedback, 
                         dict(feedback_final='This is a test feedback.',
                              future_participation=True), 
                         check_html=False)
            yield Submission(MyPage, 
                        check_html=False)