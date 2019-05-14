from django.contrib import admin
from django.conf import settings

from meetup_bot.fetcher.fetcher import MeetupFetcher

from .models import Member, Event, EventAttendance, AttendancePoint


class CustomModelAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(CustomModelAdmin, self).__init__(model, admin_site)


class EventAdmin(CustomModelAdmin):
    actions = ['update_attendance']

    def update_attendance(self, request, queryset):
        fetcher = MeetupFetcher(
            settings.MEETUP_DEFAULT_USER,  # Later on we can change it to logged-in user
            settings.MEETUP_CLIENT_ID,
            settings.MEETUP_CLIENT_SECRET,
            settings.MEETUP_NAME,
        )
        for event in queryset.all():
            attendance_list = fetcher.attendance_list(event.meetup_id)
            for attendance in attendance_list:
                # TODO: Performance - use bulk create
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

    update_attendance.short_description = 'Update attendance for events'


admin.site.register(Member, CustomModelAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(AttendancePoint, CustomModelAdmin)
admin.site.register(EventAttendance, CustomModelAdmin)
