from django.urls import path

from . import views

urlpatterns = [
    path('aa/<int:event_id>', views.authorize_attendance, name='authorize_attendance'),
    path('mark-attendance/<int:event_id>', views.mark_attendance, name='mark_attendance'),
    path('sync-events', views.sync_events, name='sync_events'),
    path('paper-attendance/<int:event_id>', views.paper_attendance, name='paper_attendance'),
]
