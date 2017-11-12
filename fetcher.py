import requests


class MeetupFetcher(object):
    def __init__(self, meetup_urlname):
        self._url_name = meetup_urlname
        self._session = requests.Session()

    def last_events_ids(self, number_of_events=1):
        return [244339632]

    def members(self):
        """ Fetch all meetup members """
        return []

    def attendance(self, event, member):
        """ Returns attendance status for the member in the given event """
        return {}
