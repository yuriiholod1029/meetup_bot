
class Evaluator(object):
    def __init__(self, config, fetch, num_of_events=1):
        self._config = config
        self._fetch = fetch
        self._num_of_events = num_of_events

    def evaluate_by_events(self, reputation_class):
        events_ids = self._fetch.last_events_ids(self._num_of_events)
        reputation = reputation_class(self._fetch.members())

        for event_id in events_ids:
            self._evaluate_event(reputation, event_id)

        return reputation

    def evaluate_single_event(self, reputation_class, event_id):
        reputation = reputation_class(self._fetch.members())

        self._evaluate_event(reputation, event_id)

        return reputation

    def _evaluate_event(self, reputation_collector, event_id):
        attendances = self._fetch.attendance_list(event_id)
        for attendance in attendances:
            if attendance["member"]["id"] == 0:
                continue  # case when member is a former member
            reputation_affect = self._evaluate_attendance(attendance["status"])
            reputation_collector.update_member_evaluation(attendance["member"]["id"], reputation_affect)

    def _evaluate_attendance(self, attendance_status):
        return self._config.evaluate(attendance_status)
