from django.urls import path

from . import views

urlpatterns = [
    path('authorize-attendance', views.authorize_attendance),
    path('mark-attendance', views.mark_attendance, name='mark_attendance'),
]
