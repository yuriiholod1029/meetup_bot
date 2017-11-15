import unittest

from reputation import Reputation


class ReputationTests(unittest.TestCase):
    def test_dump_to_csv_string(self):
        reputation = Reputation({})
        reputation._reputations = {
            1: {"name": "John", "points": 1},
            2: {"name": "Sarah", "points": 2},
            3: {"name": "Pavel", "points": 3},
            4: {"name": "Anthony", "points": -2},
            5: {"name": "Steve", "points": -1},
        }

        dump = reputation.dump_to_csv(sort=True)

        self.assertEqual(dump, "\n".join(
            ["Pavel,3", "Sarah,2", "John,1", "Steve,-1", "Anthony,-2"]
        ))
