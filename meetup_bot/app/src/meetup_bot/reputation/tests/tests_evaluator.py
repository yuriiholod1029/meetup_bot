from unittest import TestCase
from unittest.mock import Mock

from meetup_bot.app.src.meetup_bot.reputation.config import JsonFileConfig
from meetup_bot.app.src.meetup_bot.reputation.evaluator import Evaluator
from meetup_bot.app.src.meetup_bot.reputation.fetcher import MeetupFetcher
from meetup_bot.app.src.meetup_bot.reputation.reputation import Reputation


ATTENDED = "attended"
ABSENT = "absent"
YES = "yes"
NO = "no"


class EvaluatorTests(TestCase):
    def setUp(self):
        self.configuration = JsonFileConfig("foobar")
        self.fetcher = Mock(spec=MeetupFetcher)

    def test_one_event(self):
        ALICE, BOB, CINDY = self._ids_range(3)

        self.configuration._config = {
            "yes, attended": 1,
            "no, attended": -1,
            "yes, absent": -3,
        }
        self.num_of_events = 3
        self.members = zip(self._ids_range(3), ["Alice", "Bob", "Cindy"])

        self.fetcher.last_events_ids = Mock(return_value=range(self.num_of_events))
        self.fetcher.members = Mock(return_value=self.members)

        def side_effect(event_num):
            selector = {
                0: [
                    {"member": {"id": ALICE}, "rsvp": {"response": YES}, "status": ATTENDED},
                    {"member": {"id": BOB}, "rsvp": {"response": NO}, "status": ABSENT},
                    {"member": {"id": CINDY}, "status": ABSENT},
                ],
                1: [
                    {"member": {"id": ALICE}, "rsvp": {"response": YES}, "status": ATTENDED},
                    {"member": {"id": BOB}, "rsvp": {"response": NO}, "status": ABSENT},
                    {"member": {"id": CINDY}, "rsvp": {"response": NO}, "status": ATTENDED},
                ],
                2: [
                    {"member": {"id": ALICE}, "rsvp": {"response": YES}, "status": ATTENDED},
                    {"member": {"id": BOB}, "rsvp": {"response": YES}, "status": ATTENDED},
                    {"member": {"id": CINDY}, "rsvp": {"response": YES}, "status": ABSENT},
                ],
            }
            return selector[event_num]
        self.fetcher.attendance_list = Mock(side_effect=side_effect)

        evaluator = Evaluator(self.configuration, self.fetcher, self.num_of_events)
        reputation = evaluator.evaluate_by_events(Reputation)

        self.assertEqual(len(reputation._reputations.items()), 3)
        self.assertEqual(reputation._reputations[ALICE]["points"], 3)
        self.assertEqual(reputation._reputations[BOB]["points"], 1)
        self.assertEqual(reputation._reputations[CINDY]["points"], -4)

    def _ids_range(self, how_many):
        return range(100, 100 + how_many)

    def tearDown(self):
        self.fetcher.reset_mock()
