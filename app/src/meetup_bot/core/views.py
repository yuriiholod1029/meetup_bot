from django.shortcuts import render

# Create your views here.
# For finding members with total points
# eas = Member.objects.raw('''SELECT m.id, sum(ap.points) as total_points from core_eventattendance ea
#     ...:                    INNER JOIN core_member m
#     ...:                    ON m.id = ea.member_id
#     ...:                    LEFT JOIN core_attendancepoint ap
#     ...:                    ON ea.rsvp = ap.rsvp
#     ...:                    AND (ea.status = ap.status or (ea.status is null and ap.status is null))
#     ...:                    group by m.id order by total_points''')
