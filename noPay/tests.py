# myapp/tests.py

from otree.api import Bot, SubmissionMustFail
from . import *

class PlayerBot(Bot):
    def play_round(self):
        show_exit = (
            (not self.player.participant.complete_presurvey and (
                not self.player.participant.active
                or not self.player.participant.gives_consent
                or self.player.participant.failed_attention_check
                or self.player.participant.training_attempt == 0
            ))
            or (self.player.participant.complete_presurvey and (
                not self.player.participant.active or self.player.participant.away_long
            ))
        )

        if show_exit:
            yield Submission(ExitPage, dict(future_participation=True,
                                            ), check_html=False)