import urllib
import logging
from requests.exceptions import HTTPError

from django.conf import settings
from django.http.response import HttpResponse, HttpResponseServerError
from django.shortcuts import redirect, reverse, get_object_or_404

from meetup_bot.fetcher.utils import generate_token, get_default_fetcher
from meetup_bot.fetcher.fetcher import MeetupClient, MeetupFetcher

from .models import Member, Event, RSVPStatus
from .tasks import fetch_events

logger = logging.getLogger(__name__)


def authorize_attendance(request, event_id):
    auth_url = 'https://secure.meetup.com/oauth2/authorize'
    params = dict(
        client_id=settings.MEETUP_CLIENT_ID,
        response_type='code',
        redirect_uri=request.build_absolute_uri(
            location=reverse('mark_attendance', kwargs=dict(event_id=event_id)),
        ),
    )
    encoded_params = urllib.parse.urlencode(params)
    redirect_url = f'{auth_url}?{encoded_params}'
    logger.info("Redirect Url: %s", redirect_url)
    return redirect(redirect_url)


def mark_attendance(request, event_id):
    logger.info("Request attendance for event: %s", event_id)
    get_object_or_404(Event, meetup_id=event_id)
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    if state:
        logger.error("Error from Meetup authentication: state: %s, error: %s", state, error)
        return HttpResponse(error)
    redirect_uri = request.build_absolute_uri('?')
    token_dict = generate_token(code, redirect_uri)
    client = MeetupClient(settings.MEETUP_CLIENT_ID, settings.MEETUP_CLIENT_SECRET, token_dict)
    fetcher = MeetupFetcher(client, settings.MEETUP_NAME)
    # get the member id, and their details
    member_detail = fetcher.my_member_detail()
    # check if member is part of our members (from our database)
    member_id = member_detail['id']
    get_object_or_404(Member, meetup_id=member_id)
    # TODO: Should we check if this user is rsvp yes in the event
    # mark attendance using default fetcher
    default_fetcher = get_default_fetcher()
    try:
        default_fetcher.mark_attendance(event_id, member_id, RSVPStatus.ATTENDED)
    except HTTPError:
        logger.exception('Error from Meetup api when marking attendance for: %s', member_id)
        return HttpResponseServerError('There is some problem. Please contact organizers.')
    return HttpResponse('Your attendance is marked successfully. Thanks for attending.')


def sync_events(request):
    fetch_events.delay()
    return HttpResponse('Events sync started')
