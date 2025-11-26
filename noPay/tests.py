# myapp/tests.py

from otree.api import Bot, SubmissionMustFail
from . import *

class PlayerBot(Bot):
    def play_round(self):
        # Only yield ExitPage if it's actually displayed for this participant
        if ExitPage.is_displayed(self.player):
            yield Submission(ExitPage, dict(feedback_final='Bot test feedback'), check_html=False)