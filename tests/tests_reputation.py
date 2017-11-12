import unittest

from reputation import Reputation


class ReputationTests(unittest.TestCase):
    def test_dump_to_csv_string(self):
        reputation = Reputation({})
        reputation._reputations = {
            "John": 1,
            "Sarah": 2,
            "Pavel": 3,
            "Anthony": -2,
            "Steve": -1
        }

        dump = reputation.dump_to_csv(sort=True)

        self.assertEqual(dump, "\n".join(
            ["Pavel,3", "Sarah,2", "John,1", "Steve,-1", "Anthony,-2"]
        ))
