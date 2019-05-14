from datetime import datetime

from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils import timezone

from meetup_bot.celery import app
from meetup_bot.fetcher.fetcher import MeetupFetcher

from meetup_bot.core.models import Event

logger = get_task_logger(__name__)


def get_timezone_aware_datetime_from_timestamp(timestamp_in_millis):
    timestamp = int(timestamp_in_millis / 1000)
    return timezone.make_aware(datetime.fromtimestamp(timestamp))


@app.task
def fetch_events():
    fetcher = MeetupFetcher(
        settings.MEETUP_DEFAULT_USER,
        settings.MEETUP_CLIENT_ID,
        settings.MEETUP_CLIENT_SECRET,
        settings.MEETUP_NAME,
    )
    extra_params = {'status': 'past,upcoming'}
    # TODO: Get only events which are not yet created

    for event in fetcher.events(**extra_params):
        # Needs to be tested
        created = get_timezone_aware_datetime_from_timestamp(int(event['created']))
        Event.objects.update_or_create(meetup_id=event['id'], defaults=dict(created=created))
