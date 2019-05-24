from django.db import models


class Member(models.Model):
    meetup_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=512)


class Event(models.Model):
    meetup_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(blank=True, max_length=256)
    created = models.DateTimeField(db_index=True)
    max_allowed = models.IntegerField(null=True, blank=True)
    # TODO: Event details (like date, venue and other things)


class RSVPStatus(models.Model):
    RSVP_YES = 'yes'
    RSVP_NO = 'no'

    RSVP_CHOICES = (
        (RSVP_YES, RSVP_YES),
        (RSVP_NO, RSVP_NO),
    )

    ATTENDED = 'attended'
    NOSHOW = 'noshow'
    ABSENT = 'absent'

    STATUS_CHOICES = (
        (ATTENDED, ATTENDED),
        (NOSHOW, NOSHOW),
        (ABSENT, ABSENT),
    )

    rsvp = models.CharField(max_length=3, choices=RSVP_CHOICES, db_index=True)
    status = models.CharField(max_length=32, null=True, blank=True, choices=STATUS_CHOICES, db_index=True)

    class Meta:
        abstract = True


class AttendancePoint(RSVPStatus):
    points = models.IntegerField(help_text='Points to be added (negative if you want to deduct)')


class EventAttendance(RSVPStatus):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    override_points = models.IntegerField(
        null=True,
        blank=True,
        help_text='This will be used to override points irrespective of status and rsvp'
    )
    # TODO: do we need to keep reason in case we have forgiven of a no show?
