from django.conf import settings
from meetup_bot.fetcher.fetcher import MeetupFetcher, MeetupClient


def get_default_fetcher():
    client = MeetupClient.from_username(
        settings.MEETUP_DEFAULT_USER,  # Later on we can change it to logged-in user
        settings.MEETUP_CLIENT_ID,
        settings.MEETUP_CLIENT_SECRET,
    )
    return MeetupFetcher(client, settings.MEETUP_NAME)
