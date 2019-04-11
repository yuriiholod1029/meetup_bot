from django.db import models

from model_utils import Choices


class Member(models.Model):

    meetupcom_id = models.IntegerField(blank=False, null=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    reputation = models.IntegerField(blank=False, null=False, default=0)


class Event(models.Model):

    meetupcom_id = models.IntegerField(blank=False, null=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    members = models.ManyToManyField(Member, 'events', through='Attendance')


class Attendance(models.Model):

    RESPONSE = Choices('yes', 'no', 'whitelist')
    STATUS = Choices('attended', 'noshow', 'absent')

    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    response = models.CharField(max_length=15, blank=False, null=False, choices=RESPONSE)
    status = models.CharField(max_length=15, blank=True, null=True, default=None, choices=STATUS)
    accounted = models.BooleanField(blank=True, null=False, default=False)
