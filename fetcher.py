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
        response = self._session.get(self.EVENTS_URL_FORMAT.format(self._meetup_name), params={"status": "past", 'key': self._get_token()})
        self._check_response(response)
        return [event["id"] for event in sorted(response.json(), key=lambda e: int(e["created"]))[-number_of_events:]]

    def members(self):
        response = self._session.get(self.MEMBERS_URL_FORMAT.format(self._meetup_name), params={'key': self._get_token()})
        self._check_response(response)
        return [(member["id"], member["name"]) for member in response.json()]

    def attendance_list(self, event_id):
        response = self._session.get(self.ATTENDANCES_URL_FORMAT.format(self._meetup_name, event_id), params={'key': self._get_token()})
        self._check_response(response)
        return response.json()

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
