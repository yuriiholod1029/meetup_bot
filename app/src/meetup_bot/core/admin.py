from django.contrib import admin
from django.contrib.messages import SUCCESS, ERROR
from django.conf import settings

from requests import HTTPError

from meetup_bot.fetcher.fetcher import MeetupFetcher

from .models import Member, Event, EventAttendance, AttendancePoint


class CustomModelAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(CustomModelAdmin, self).__init__(model, admin_site)


class EventAdmin(CustomModelAdmin):
    actions = ['update_attendance', 'preview_waitlist']

    def update_attendance(self, request, queryset):
        fetcher = MeetupFetcher(
            settings.MEETUP_DEFAULT_USER,  # Later on we can change it to logged-in user
            settings.MEETUP_CLIENT_ID,
            settings.MEETUP_CLIENT_SECRET,
            settings.MEETUP_NAME,
        )
        for event in queryset.all():
            # TODO: Move this function to a separate module
            try:
                attendance_list = fetcher.attendance_list(event.meetup_id)
            except HTTPError:
                self.message_user(request, f'Cannot update attendance for event: {event.meetup_id}', ERROR)
                continue
            for attendance in attendance_list:
                # TODO: Performance - use bulk create
                if 'rsvp' not in attendance:
                    continue
                member, created = Member.objects.get_or_create(meetup_id=attendance['member']['id'], defaults={
                    'name': attendance['member']['name']
                })
                EventAttendance.objects.update_or_create(
                    event=event,
                    member=member,
                    defaults=dict(
                        rsvp=attendance['rsvp']['response'],
                        status=attendance.get('status'),
                    ),
                )
        self.message_user(request, 'Attendance updated for selected events', SUCCESS)

    update_attendance.short_description = 'Update attendance for events'

    def preview_waitlist(self, request, queryset):
        fetcher = MeetupFetcher(
            settings.MEETUP_DEFAULT_USER,  # Later on we can change it to logged-in user
            settings.MEETUP_CLIENT_ID,
            settings.MEETUP_CLIENT_SECRET,
            settings.MEETUP_NAME,
        )
        for event in queryset.all():
            waitlist_members = fetcher.waitlist_rsvps(event.meetup_id)
            waitlist_members_str = ','.join([str(m) for m in waitlist_members])
            members = Member.objects.raw(f'''SELECT m.id, sum(
                                                CASE
                                                WHEN ea.override_points is not null
                                                THEN ea.override_points
                                                ELSE ap.points
                                                END) as total_points
                                             FROM core_eventattendance ea
                                             INNER JOIN core_member m
                                             ON m.id = ea.member_id
                                             LEFT JOIN core_attendancepoint ap
                                             ON ea.rsvp = ap.rsvp
                                             WHERE (ea.status = ap.status or (ea.status is null and ap.status is null))
                                             AND m.meetup_id in ({waitlist_members_str})
                                             GROUP BY m.id ORDER BY total_points DESC''')
            self.message_user(
                request,
                [(m.name, m.total_points) for m in members],
                SUCCESS,
            )

    preview_waitlist.short_description = 'Preview Waitlist for event'


admin.site.register(Member, CustomModelAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(AttendancePoint, CustomModelAdmin)
admin.site.register(EventAttendance, CustomModelAdmin)
