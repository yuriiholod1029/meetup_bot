from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admin.sites import site
from django.urls import include, path

urlpatterns = [
    path('admin/', site.urls),
    path('', include('django.contrib.auth.urls')),
    path('fetcher/', include('meetup_bot.fetcher.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
