from django.urls import path

from . import views

urlpatterns = [
    path('authorize/<str:username>', views.authorize_user),
]
