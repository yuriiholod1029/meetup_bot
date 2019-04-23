from django.db import models


class MeetupToken(models.Model):
    # TODO: Should we use logged in user or make it part of redirect url?
    username = models.CharField(max_length=512)
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=512)
    token_type = models.CharField(max_length=128)
    expires_in = models.IntegerField()
    expires_at = models.DateTimeField()

    def token_dict(self, client_id, client_secret):
        return dict(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            client_id=client_id,
            client_secret=client_secret,
        )
