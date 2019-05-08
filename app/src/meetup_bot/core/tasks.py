from celery.utils.log import get_task_logger
from django.conf import settings

from meetup_bot.celery import app
from meetup_bot.fetcher.fetcher import MeetupFetcher

from meetup_bot.core.models import Event

logger = get_task_logger(__name__)


@app.task
def fetch_events():
    return
    fetcher = MeetupFetcher(
        settings.MEETUP_DEFAULT_USER,  # Later on we can change it to logged-in user
        settings.MEETUP_CLIENT_ID,
        settings.MEETUP_CLIENT_SECRET,
        settings.MEETUP_NAME,
    )
    for event in fetcher.past_events():
         pass


