
class Evaluator(object):
    def __init__(self, config, fetch, num_of_events=1):
        self._config = config
        self._fetch = fetch
        self._num_of_events = num_of_events

    def evaluate_members(self, reputation_class):
        members = self._fetch.members()
        events_ids = self._fetch.last_events_ids(self._num_of_events)
        reputation = reputation_class(members)

        for member in members:
            for event in events_ids:
                attendance_status = self._fetch.attendance(event, member)
                reputation_affect = self._evaluate_attendance(attendance_status)
                reputation.update_member_evaluation(member, reputation_affect)

        return reputation

    def _evaluate_attendance(self, attendance_status):
        return self._config.evaluate(attendance_status)  # TODO this is not sufficient
