from django.conf import settings
from requests_oauthlib import OAuth2Session

from meetup_bot.fetcher.fetcher import MeetupFetcher, MeetupClient


def get_default_fetcher():
    client = MeetupClient.from_username(
        settings.MEETUP_DEFAULT_USER,  # Later on we can change it to logged-in user
        settings.MEETUP_CLIENT_ID,
        settings.MEETUP_CLIENT_SECRET,
    )
    return MeetupFetcher(client, settings.MEETUP_NAME)


def generate_token(code, redirect_uri):
    session = OAuth2Session(settings.MEETUP_CLIENT_ID, redirect_uri=redirect_uri)
    token_dict = session.fetch_token(
        token_url='https://secure.meetup.com/oauth2/access',
        include_client_id=True,
        client_secret=settings.MEETUP_CLIENT_SECRET,
        code=code,
    )
    return token_dict
