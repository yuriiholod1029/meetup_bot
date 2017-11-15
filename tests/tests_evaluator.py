from unittest import TestCase
from unittest.mock import Mock

from config import JsonFileConfig
from evaluator import Evaluator
from fetcher import MeetupFetcher
from reputation import Reputation


ATTENDED = "attended"
ABSENT = "absent"
NOSHOW = "noshow"


class EvaluatorTests(TestCase):
    def setUp(self):
        self.configuration = JsonFileConfig("foobar")
        self.fetcher = Mock(spec=MeetupFetcher)

    def test_one_event(self):
        self.configuration._config = {
            "attended": 1,
            "absent": 0,
            "noshow": -3,
        }
        self.num_of_events = 3
        self.members = ["Alice", "Bob", "Cindy"]

        self.fetcher.last_events_ids = Mock(return_value=range(self.num_of_events))
        self.fetcher.members = Mock(return_value=self.members)

        def side_effect(event_num):
            ALICE = "Alice"
            BOB = "Bob"
            CINDY = "Cindy"
            selector = {
                0: {
                    ALICE: {"status": ATTENDED},
                    BOB: {"status": ABSENT},
                    CINDY: {"status": NOSHOW},
                },
                1: {
                    ALICE: {"status": ATTENDED},
                    BOB: {"status": NOSHOW},
                    CINDY: {"status": NOSHOW},
                },
                2: {
                    ALICE: {"status": ATTENDED},
                    BOB: {"status": ATTENDED},
                    CINDY: {"status": ABSENT},
                },
            }
            return selector[event_num]
        self.fetcher.attendance_list = Mock(side_effect=side_effect)

        evaluator = Evaluator(self.configuration, self.fetcher, self.num_of_events)
        reputation = evaluator.evaluate_by_events(Reputation)

        self.assertEqual(len(reputation._reputations.items()), 3)
        self.assertEqual(reputation._reputations["Alice"], 3)
        self.assertEqual(reputation._reputations["Bob"], -2)
        self.assertEqual(reputation._reputations["Cindy"], -6)

    def tearDown(self):
        self.fetcher.reset_mock()
