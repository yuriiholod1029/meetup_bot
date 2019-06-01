from django.urls import path

from . import views

urlpatterns = [
    path('authorize-attendance/<int:event_id>', views.authorize_attendance),
    path('mark-attendance/<int:event_id>', views.mark_attendance, name='mark_attendance'),
]
