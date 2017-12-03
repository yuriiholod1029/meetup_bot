from requests import Session


class MeetupFetcher(object):
    EVENTS_URL_FORMAT = "https://api.meetup.com/{0}/events"
    MEMBERS_URL_FORMAT = "https://api.meetup.com/{0}/members"
    ATTENDANCES_URL_FORMAT = "https://api.meetup.com/{0}/events/{1}/attendance"

    def __init__(self, meetup_name, token_file=".token"):
        self._headers = {}
        self._meetup_name = meetup_name

        self._session = Session()
        self._session.headers.update(self._headers)
        self.token_file = token_file

    def last_events_ids(self, number_of_events=1):
        params = {"status": "past", 'key': self._get_token()}
        events = (
            event
            for response in self._all_responses(
                self.EVENTS_URL_FORMAT.format(self._meetup_name),
                params=params
            )
            for event in response.json()
        )
        return [event["id"] for event in sorted(events, key=lambda e: int(e["created"]))[-number_of_events:]]

    def members(self):
        params = {'key': self._get_token()}
        members = [
            (member["id"], member["name"])
            for response in self._all_responses(self.MEMBERS_URL_FORMAT.format(self._meetup_name), params=params)
            for member in response.json()
        ]
        return members

    def attendance_list(self, event_id):
        params = {'key': self._get_token()}
        return [
            attendance
            for response in self._all_responses(
                self.ATTENDANCES_URL_FORMAT.format(self._meetup_name, event_id), params=params)
            for attendance in response.json()
        ]

    def _all_responses(self, initial_request, **kwargs):
        response = self._session.get(initial_request, **kwargs)
        self._check_response(response)
        yield response
        while response.links.get('next'):
            response = self._session.get(response.links['next']['url'], **kwargs)
            self._check_response(response)
            yield response

    def _get_token(self):
        try:
            with open(self.token_file) as app_file:
                return app_file.readline().strip()
        except FileNotFoundError:
            raise Exception("Please create file '.token' with app token")

    def _check_response(self, response):
        if response.status_code == 400:
            raise Exception("400: {0}".format(response.content))
        elif response.status_code != 200:
            raise Exception("Status code {0} is different than 200, something went wrong.".format(response.status_code))
