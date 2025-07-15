# myapp/tests.py

from otree.api import Bot, SubmissionMustFail
from . import Page

class PlayerBot(Bot):
    def play_round(self):
        yield Page.GroupingWaitPage, dict(
    
        )