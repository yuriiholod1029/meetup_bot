
class Evaluator(object):
    def __init__(self, config, fetch, num_of_events=1):
        self._config = config
        self._fetch = fetch
        self._num_of_events = num_of_events

    def evaluate_by_events(self, reputation_class):
        events_ids = self._fetch.last_events_ids(self._num_of_events)
        reputation = reputation_class(self._fetch.members())

        for event in events_ids:
            attendances = self._fetch.attendance_list(event)
            for attendance in attendances:
                reputation_affect = self._evaluate_attendance(attendance["status"])
                reputation.update_member_evaluation(attendance["member"]["id"], reputation_affect)

        return reputation

    def _evaluate_attendance(self, attendance_status):
        return self._config.evaluate(attendance_status)
