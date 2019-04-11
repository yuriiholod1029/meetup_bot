import logging
from typing import Dict


class Evaluator(object):

    def __init__(self, reputation_score: Dict, fetch, num_of_events=1):
        self.REPUTATION_SCORE = reputation_score
        self._fetch = fetch
        self._num_of_events = num_of_events

    def evaluate_by_events(self, reputation_class):
        events_ids = self._fetch.last_events_ids(self._num_of_events)
        reputation = reputation_class(self._fetch.members())

        for event_id in events_ids:
            self._evaluate_event(reputation, event_id)

        return reputation

    def _evaluate_event(self, reputation_collector, event_id):
        attendances = self._fetch.attendance_list(event_id)
        for attendance in attendances:
            member = attendance.get("member")
            if member is None:
                continue  # future meetup, no attendance list?
            if attendance["member"]["id"] == 0:
                continue  # case when member is a former member
            reputation_affect = self._evaluate_attendance(attendance)
            reputation_collector.update_member_evaluation(attendance["member"]["id"], reputation_affect)

    def _evaluate_attendance(self, attendance: Dict):
        rsvp = attendance.get('rsvp')
        if rsvp is None:
            return 0  # case when user did not declared any attendance before event

        attendance_response = rsvp['response']
        attendance_status = attendance_response.get('status')

        attendance_code = f'{attendance_response}, {attendance_status}'
        score = self.REPUTATION_SCORE.get(attendance_code)

        if score is None:
            logging.warning(f'No score for `{attendance_code}` attendance code')
            return 0

        return score
