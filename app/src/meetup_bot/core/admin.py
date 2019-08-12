from django.contrib import admin
from django.contrib.messages import SUCCESS, ERROR
from django.shortcuts import reverse
from django.utils.html import format_html

from requests import HTTPError

from meetup_bot.fetcher.utils import get_default_fetcher
from .models import Member, Event, EventAttendance, AttendancePoint


class CustomModelAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(CustomModelAdmin, self).__init__(model, admin_site)


def get_waitlist_members_for_event(fetcher, event_id):
    waitlist_members = fetcher.waitlist_rsvps(event_id)
    return waitlist_members


def get_points_for_waitlist_members(waitlist_members):
    waitlist_members_str = ','.join([str(m['id']) for m in waitlist_members])
    members = Member.objects.raw(
        f'''SELECT m.id, sum(
            CASE
            WHEN ea.override_points is not null
            THEN ea.override_points
            WHEN ap.points is not null
            THEN ap.points
            ELSE 0
            END) as total_points
         FROM core_member m
         LEFT JOIN core_eventattendance ea
         ON m.id = ea.member_id
         LEFT JOIN core_attendancepoint ap
         ON ea.rsvp = ap.rsvp
         AND (ea.status = ap.status or (ea.status is null and ap.status is null))
         WHERE m.meetup_id in ({waitlist_members_str})
         GROUP BY m.id ORDER BY total_points DESC, random()'''
    )
    return members


class EventAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields] + ['paper_attendance_link']
        super().__init__(model, admin_site)

    actions = ['update_attendance', 'preview_waitlist', 'waitlist_to_yes']

    def update_attendance(self, request, queryset):
        fetcher = get_default_fetcher()
        for event in queryset.all():
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
        fetcher = get_default_fetcher()
        for event in queryset.all():
            waitlist_members = get_waitlist_members_for_event(fetcher, event.meetup_id)
            if not waitlist_members:
                self.message_user(request, f'No waitlist members for meetup: {event.meetup_id}', SUCCESS)
                continue
            members = get_points_for_waitlist_members(waitlist_members)
            self.message_user(
                request,
                [(m.name, m.total_points) for m in members],
                SUCCESS,
            )

    preview_waitlist.short_description = 'Preview Waitlist for event'

    def waitlist_to_yes(self, request, queryset):
        fetcher = get_default_fetcher()
        for event in queryset.all():
            if event.max_allowed is None:
                self.message_user(request, f'Please set Max allowed for meetup: {event.meetup_id}', ERROR)
                continue
            rsvps_list = fetcher.rsvps(event.meetup_id)
            rsvps_list = [r for r in rsvps_list]
            # get total members with yes.
            yes_members = [
                rsvp_dict['member']
                for rsvp_dict in rsvps_list
                if rsvp_dict['response'] == 'yes' and 'id' in rsvp_dict['member']
            ]
            if len(yes_members) >= event.max_allowed:
                self.message_user(request, f'Yes members already full for meetup: {event.meetup_id}', SUCCESS)
                continue

            waitlist_members = [
                rsvp_dict['member']
                for rsvp_dict in rsvps_list
                if rsvp_dict['response'] == 'waitlist' and 'id' in rsvp_dict['member']
            ]
            if not waitlist_members:
                self.message_user(request, f'No waitlist members for meetup: {event.meetup_id}', SUCCESS)
                continue
            members = get_points_for_waitlist_members(waitlist_members)

            num_members_allow = event.max_allowed - len(yes_members)
            members_updated = []
            for i in range(num_members_allow):
                fetcher.update_rsvp(event.meetup_id, members[i].meetup_id)
                members_updated.append(members[i].name)
            self.message_user(
                request,
                f'waitlist members: {members_updated} updated to yes for meetup: {event.meetup_id}\n',
                SUCCESS
            )

    waitlist_to_yes.short_description = 'Mark waitlist members to yes'

    def paper_attendance_link(self, event):
        link = reverse(
            'paper_attendance',
            kwargs={
                'event_id': event.id,
            },
        )
        return format_html(
            '<a href="{link}" title="{name}" target="_blank">Print RSVP list</a> ',
            link=link,
            name=event.name,
        )
    paper_attendance_link.short_description = 'Paper Attendance'


class MemberAdmin(CustomModelAdmin):
    search_fields = ['name']


admin.site.register(Member, MemberAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(AttendancePoint, CustomModelAdmin)
admin.site.register(EventAttendance, CustomModelAdmin)
