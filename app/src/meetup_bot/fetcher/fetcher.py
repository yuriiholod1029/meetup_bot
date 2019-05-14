import logging
import time

from requests_oauthlib import OAuth2Session

from .models import MeetupToken

logger = logging.getLogger(__name__)


class MeetupFetcher(object):
    EVENTS_URL_FORMAT = "https://api.meetup.com/{0}/events"
    MEMBERS_URL_FORMAT = "https://api.meetup.com/{0}/members"
    ATTENDANCES_URL_FORMAT = "https://api.meetup.com/{0}/events/{1}/attendance"
    RSVPS_URL = "https://api.meetup.com/2/rsvps"
    REFRESH_URL = 'https://secure.meetup.com/oauth2/access'

    def __init__(self, username, client_id, client_secret, meetup_name):
        self._headers = {}
        self._meetup_name = meetup_name
        # Should we pass meetup token object instead of username
        meetup_token_obj = MeetupToken.objects.filter(username=username).first()
        if not meetup_token_obj:
            raise Exception('Please authorize first to use')

        self._meetup_token_obj = meetup_token_obj
        self._client = self._get_client(client_id, client_secret)

    def _save_meetup_token(self, token_dict):
        # TODO: Move this to model
        self._meetup_token_obj.access_token = token_dict['access_token']
        self._meetup_token_obj.expires_at = token_dict['expires_at']
        self._meetup_token_obj.expires_in = token_dict['expires_in']
        self._meetup_token_obj.save(update_fields=['access_token', 'expires_at', 'expires_in'])

    def _get_client(self, client_id, client_secret):
        token_dict = self._meetup_token_obj.token_dict
        extra = dict(
            client_id=client_id,
            client_secret=client_secret,
        )
        client = OAuth2Session(
            client_id,
            token=token_dict,
            auto_refresh_url=self.REFRESH_URL,
            auto_refresh_kwargs=extra,
            token_updater=self._save_meetup_token,
        )
        return client

    def events(self, **extra_params):
        # Default it will show only upcoming meetups
        return self._events_according_to_params(extra_params)

    def last_events_ids(self, number_of_events=1):
        extra_params = {"status": "past"}
        events = self.events(**extra_params)
        return [event["id"] for event in sorted(events, key=lambda e: int(e["created"]))[-number_of_events:]]

    def raw_members(self):
        params = {}
        members = [
            member
            for response in self._all_responses(self.MEMBERS_URL_FORMAT.format(self._meetup_name), params=params)
            for member in response.json()
        ]
        logger.info('member count: %i', len(members))
        return members

    def members(self):
        members = [
            (member["id"], member["name"])
            for member in self.raw_members()
        ]
        return members

    def attendance_list(self, event_id):
        params = {'filter': 'all'}
        return self._attendances_list_according_to_params(event_id, params)

    def waitlist_rsvps(self, event_id):
        rsvps_list = self.rsvps(event_id)
        return [rsvp_dict['member']['member_id'] for rsvp_dict in rsvps_list if rsvp_dict['response'] == 'waitlist']

    def rsvps(self, event_id, **extra_params):
        params = {
            'event_id': event_id,
            **extra_params,
        }
        return self._rsvps_according_to_params(params)

    def _rsvps_according_to_params(self, params):
        return (result for results in self._all_responses_v2(self.RSVPS_URL, params=params) for result in results)

    def _events_according_to_params(self, params):
        return (
            event
            for response in self._all_responses(
                self.EVENTS_URL_FORMAT.format(self._meetup_name),
                params=params,
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
            response = self._client.get(request, **kwargs)
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

    def _all_responses_v2(self, initial_request, **kwargs):
        response = self._get(initial_request, **kwargs)
        yield response.json()['results']
        while response.json()['meta']['next']:
            response = self._get(response.json()['meta']['next'], **kwargs)
            yield response.json()['results']
