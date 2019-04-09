import logging

from requests import Session


logger = logging.getLogger(__name__)


class MeetupFetcher(object):
    EVENTS_URL_FORMAT = "https://api.meetup.com/{0}/events"
    MEMBERS_URL_FORMAT = "https://api.meetup.com/{0}/members"
    ATTENDANCES_URL_FORMAT = "https://api.meetup.com/{0}/events/{1}/attendance"

    def __init__(self, meetup_name, token):
        self._headers = {}
        self._meetup_name = meetup_name

        self._session = Session()
        self._session.headers.update(self._headers)
        self._token = token

    def last_events_ids(self, number_of_events=1):
        params = {"status": "past", 'key': self._token}
        events = self._events_according_to_params(params)
        return [event["id"] for event in sorted(events, key=lambda e: int(e["created"]))[-number_of_events:]]

    def raw_members(self):
        params = {'key': self._token}
        members = [
            member
            for response in self._all_responses(self.MEMBERS_URL_FORMAT.format(self._meetup_name), params=params)
            for member in response.json()
        ]
        logger.info('member count: %i', len(members))
        return members

    def members(self):
        params = {'key': self._token}
        members = [
            (member["id"], member["name"])
            for member in self.raw_members()
        ]
        return members

    def attendance_list(self, event_id):
        params = {'filter': 'all', 'key': self._token}
        return self._attendances_list_according_to_params(event_id, params)

    def _events_according_to_params(self, params):
        return (
            event
            for response in self._all_responses(
                self.EVENTS_URL_FORMAT.format(self._meetup_name),
                params=params
            )
            for event in response.json()
        )

    def _attendances_list_according_to_params(self, event_id, params):
        return [
            attendance
            for response in self._all_responses(
                self.ATTENDANCES_URL_FORMAT.format(self._meetup_name, event_id), params=params)
            for attendance in response.json()
        ]

    def _get(self, request, **kwargs):
        while 1:
            response = self._session.get(request, **kwargs)
            if response.status_code == 429:
                logger.info('need to sleep %s', response.headers.get('X-RateLimit-Reset'))
                time.sleep(
                    max(  # to prevent accidental excessive CPU consumption if meetup rate limiter fails
                        float(
                            response.headers.get(
                                'X-RateLimit-Reset',
                                'missing header!'
                            )
                        ),
                        1
                    )
                )
                continue
            response.raise_for_status()
            return response

    def _all_responses(self, initial_request, **kwargs):
        response = self._get(initial_request, **kwargs)
        yield response
        while response.links.get('next'):
            response = self._get(response.links['next']['url'], **kwargs)
            yield response
