
class Reputation(object):
    def __init__(self, members):
        self._reputations = {mem_id: {"name": name, "points": 0} for mem_id, name in members}

    def update_member_evaluation(self, member_id, points):
        self._reputations[member_id]["points"] += points

    def dump_to_csv(self, sort=True):
        reputations_items = sorted(
            [item for item in self._reputations.items()],
            key=lambda x: x[1]["points"],
            reverse=True) if sort else self._reputations.items()
        return "\n".join("{0},{1}".format(item["name"], item["points"]) for _, item in reputations_items)
