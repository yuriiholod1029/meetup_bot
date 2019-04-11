from collections import Counter
import csv
import logging


class Reputation(object):
    def __init__(self, members):
        self._reputations = {mem_id: {"name": name, "points": 0} for mem_id, name in members}

    def update_member_evaluation(self, member_id, points):
        try:
            self._reputations[member_id]["points"] += points
        except KeyError:
            logging.warning('missing member: %s', member_id)

    def dump_to_csv(self, stream, sort=True):
        results = csv.writer(stream)
        points = Counter()
        reputations_items = sorted(
            [item for item in self._reputations.items()],
            key=lambda x: x[1]["points"],
            reverse=True) if sort else self._reputations.items()
        for _, item in reputations_items:
            points[item['points']] += 1
            results.writerow((item['name'], item['points']))
        logging.info('dumping points %s', points)
