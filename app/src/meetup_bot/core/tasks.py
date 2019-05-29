from datetime import datetime

from celery.utils.log import get_task_logger
from django.utils import timezone

from meetup_bot.celery import app
from meetup_bot.fetcher.utils import get_default_fetcher

from meetup_bot.core.models import Event, Member

logger = get_task_logger(__name__)


def get_timezone_aware_datetime_from_timestamp(timestamp_in_millis):
    timestamp = int(timestamp_in_millis / 1000)
    return timezone.make_aware(datetime.fromtimestamp(timestamp))


@app.task
def fetch_events():
    fetcher = get_default_fetcher()
    extra_params = {'status': 'past,upcoming'}
    # TODO: Get only events which are not yet created

    for event_dict in fetcher.events(**extra_params):
        created = get_timezone_aware_datetime_from_timestamp(int(event_dict['created']))
        Event.objects.update_or_create(
            meetup_id=event_dict['id'],
            defaults=dict(
                created=created,
                name=event_dict['name'],
            ),
        )


@app.task
def fetch_members():
    fetcher = get_default_fetcher()

    for member_dict in fetcher.raw_members():
        Member.objects.update_or_create(
            meetup_id=member_dict['id'],
            defaults=dict(
                name=member_dict['name'],

            ),
        )
