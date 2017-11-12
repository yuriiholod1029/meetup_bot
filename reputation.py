
class Reputation(object):
    def __init__(self, members):
        self._reputations = {mem: 0 for mem in members}

    def update_member_evaluation(self, member, points):
        self._reputations[member] += points

    def dump_to_csv(self, sort=True):
        reputations_items = sorted(self._reputations.items()) if sort else self._reputations.items()
        "\n".join("{0},{1}".format(mem, mark) for mem, mark in reputations_items)
