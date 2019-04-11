from celery.utils.log import get_task_logger

from celery import shared_task

from django.conf import settings

from meetup_bot.reputation.config import YamlFileConfig
from meetup_bot.reputation.evaluator import Evaluator
from meetup_bot.reputation.fetcher import MeetupFetcher
from meetup_bot.reputation.reputation import Reputation

logger = get_task_logger(__name__)


@shared_task()
def fetch_reputation(meetup_title: str, number_of_events: int = 10):
    """
    Build reputation report

    :param meetup_title: Meetup name, e.g. `AgileWarsaw`
    :param number_of_events: Number of last events to check, e.g. 10
    """
    fetcher = MeetupFetcher(meetup_title, token=settings.MEETUP_COM_API_TOKEN)
    reputation = Evaluator(settings.REPUTATION_SCORE, fetcher, number_of_events).evaluate_by_events(Reputation)

    with open('result.csv', 'w', encoding='utf-8') as output_stream:  # TypeError -> you are using python2.x
        reputation.dump_to_csv(output_stream)
