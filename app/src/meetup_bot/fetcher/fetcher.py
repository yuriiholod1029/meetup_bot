import logging
import time

from requests_oauthlib import OAuth2Session

from .models import MeetupToken

logger = logging.getLogger(__name__)


class MeetupClient:
    REFRESH_URL = 'https://secure.meetup.com/oauth2/access'

    def __init__(self, client_id, client_secret, token_dict, save_token):
        extra = dict(
            client_id=client_id,
            client_secret=client_secret,
        )
        self.client = OAuth2Session(
            client_id,
            token=token_dict,
            auto_refresh_url=self.REFRESH_URL,
            auto_refresh_kwargs=extra,
            token_updater=save_token,
        )

    @classmethod
    def from_username(cls, username, client_id, client_secret):
        meetup_token_obj = MeetupToken.objects.filter(username=username).first()
        if not meetup_token_obj:
            raise Exception('Please authorize first to use')

        def save_meetup_token(token_dict):
            meetup_token_obj.access_token = token_dict['access_token']
            meetup_token_obj.expires_at = token_dict['expires_at']
            meetup_token_obj.expires_in = token_dict['expires_in']
            meetup_token_obj.save(update_fields=['access_token', 'expires_at', 'expires_in'])

        token_dict = meetup_token_obj.token_dict
        return cls(client_id, client_secret, token_dict, save_meetup_token)


class MeetupFetcher(object):
    EVENTS_URL_FORMAT = "https://api.meetup.com/{0}/events"
    MEMBERS_URL_FORMAT = "https://api.meetup.com/{0}/members"
    ATTENDANCES_URL_FORMAT = "https://api.meetup.com/{0}/events/{1}/attendance"
    RSVPS_URL_FORMAT = "https://api.meetup.com/{0}/events/{1}/rsvps"
    RSVP_UPDATE_URL = 'https://api.meetup.com/2/rsvp'
    SELF_GROUPS_URL = "https://api.meetup.com/self/groups"

    def __init__(self, client, meetup_name):
        self._headers = {}
        self._meetup_name = meetup_name
        self._client = client.client

    def my_groups(self):
        return (
            group
            for response in self._all_responses(
                self.SELF_GROUPS_URL,
            )
            for group in response.json()
        )

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
            member["id"]
            for member in self.raw_members()
        ]
        return members

    def attendance_list(self, event_id):
        params = {'filter': 'all'}
        return self._attendances_list_according_to_params(event_id, params)

    def waitlist_rsvps(self, event_id):
        rsvps_list = self.rsvps(event_id)
        rsvps_list = [r for r in rsvps_list]
        return [
            rsvp_dict['member']
            for rsvp_dict in rsvps_list
            if rsvp_dict['response'] == 'waitlist' and 'id' in rsvp_dict['member']
        ]

    def rsvps(self, event_id, **params):
        return self._rsvps_according_to_params(event_id, params)

    def update_rsvp(self, event_id, member_id, rsvp_response='yes'):
        post_params = {
            'event_id': event_id,
            'member_id': member_id,
            'rsvp': rsvp_response,
        }
        return self._post(
            self.RSVP_UPDATE_URL,
            data=post_params,
        )

    def _rsvps_according_to_params(self, event_id, params):
        return (
            rsvp
            for response in self._all_responses(
                self.RSVPS_URL_FORMAT.format(self._meetup_name, event_id),
                params=params,
            )
            for rsvp in response.json()
        )

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

    def _request(self, method, url, **kwargs):
        while 1:
            response = self._client.request(method, url, **kwargs)
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

    def _get(self, url, **kwargs):
        return self._request('GET', url, **kwargs)

    def _post(self, url, **kwargs):
        return self._request('POST', url, **kwargs)

    def _all_responses(self, initial_url, **kwargs):
        response = self._get(initial_url, **kwargs)
        yield response
        while response.links.get('next'):
            response = self._get(response.links['next']['url'], **kwargs)
            yield response

    def _all_responses_v2(self, initial_url, **kwargs):
        response = self._get(initial_url, **kwargs)
        yield response.json()['results']
        while response.json()['meta']['next']:
            response = self._get(response.json()['meta']['next'], **kwargs)
            yield response.json()['results']
