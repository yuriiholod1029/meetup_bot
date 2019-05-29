import urllib

from django.conf import settings
from django.shortcuts import redirect, reverse


def authorize_attendance(request):
    auth_url = 'https://secure.meetup.com/oauth2/authorize'
    params = dict(
        client_id=settings.MEETUP_CLIENT_ID,
        response_type='code',
        redirect_uri=request.build_absolute_uri(location=reverse('mark_attendance')),
    )
    encoded_params = urllib.parse.urlencode(params)
    return redirect(f'{auth_url}?{encoded_params}')


def mark_attendance(request):
    pass
