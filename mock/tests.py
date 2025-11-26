# myapp/tests.py

from otree.api import Bot, SubmissionMustFail
from . import *
'''
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
'''

from otree.api import Bot, expect
from . import *
import random, ast

class PlayerBot(Bot):

    def play_round(self):
        # ----- Round 1 setup: fake presurvey + make sure they are eligible -----
        if self.round_number == 1:
            sce = self.session.config.get('SCE')  # same value used in creating_session
            self.participant.scenario = sce

            # Make sure these flags exist & allow app to run
            self.participant.complete_presurvey = True
            self.participant.single_group = False
            self.participant.away_long = False
            self.participant.active = True
            self.participant.failed_attention_check = False

            # Deterministic presurvey opinions for grouping:
            # players 1-2 are purple (For=1), players 3-4 are green (Against=-1)
            if self.player.id_in_subsession in [1, 2]:
                resp = 1
            else:
                resp = -1

            # all_responses must be a dict scenario->answer
            self.participant.all_responses = {sce: resp}

        # ----- After grouping wait pages, fixed network should be set -----
        # DiscussionGRPWaitPage is a WaitPage so bots don't yield it,
        # but its after_all_players_arrive has already run before the next Page.
        if self.round_number == 1 and not self.participant.single_group and not self.participant.away_long:
            # player.discussion_grp is stored as a string like "['code1','code2']"
            stored = ast.literal_eval(self.player.discussion_grp)

            pos = self.player.id_in_group
            expected_positions = C.FIXED_NETWORK[pos]
            expected_neighbors = [
                self.group.get_player_by_id(npos).participant.code
                for npos in expected_positions
            ]

            expect(set(stored), set(expected_neighbors))

        # ----- Yield non-wait pages in the correct order -----
        # AttentionCheck only if single_group (shouldn't happen for these bots)
        if AttentionCheck.is_displayed(self.player):
            yield AttentionCheck, dict(attention_check=True)

        # Nudge sequence only round 1, only not-control, only grouped
        if Nudge.is_displayed(self.player):
            # just submit something valid
            yield Submission(Nudge, dict(nudge_training=random.choice([-1, 0, 1])), check_html=False)

        if NudgeTraining.is_displayed(self.player):
            yield Submission(NudgeTraining, dict(nudge_training_two=random.choice([-1, 0, 1])), check_html=False)

        if NudgeTrainingLast.is_displayed(self.player):
            yield Submission(NudgeTrainingLast, dict(nudge_training_three=random.choice([-1, 0, 1])), check_html=False)

        # Phase3 only round 1, no form
        if Phase3.is_displayed(self.player):
            yield Phase3

        # Discussion every round for grouped players
        if Discussion.is_displayed(self.player):
            # any valid response
            yield Submission(Discussion, dict(new_response=random.choice([-1, 0, 1])), check_html=False)

        # FinalRound only last round
        if FinalRound.is_displayed(self.player):
            yield FinalRound
