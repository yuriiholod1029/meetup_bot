from datetime import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import HttpResponse
from django.utils.timezone import make_aware

from .models import MeetupToken
from .utils import generate_token


@staff_member_required
def authorize_user(request, username):
    # https://secure.meetup.com/oauth2/authorize?client_id=o5mv45qtp3b8ar39r3k9u20qe4&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Ffetcher%2Fauthorize%2Fanuj
    # TODO: Use django form for validation
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    if state:
        return HttpResponse(error)
    redirect_uri = request.build_absolute_uri('?')
    token_dict = generate_token(code, redirect_uri)
    token_dict['expires_at'] = make_aware(datetime.fromtimestamp(token_dict['expires_at']))
    MeetupToken.objects.update_or_create(username=username, defaults=token_dict)
    return HttpResponse('Token Generated. You can safely use the API for this meetup name.')
