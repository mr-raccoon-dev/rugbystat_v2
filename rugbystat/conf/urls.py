from __future__ import unicode_literals

from django.conf import settings
from django.urls import reverse_lazy
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter


from clippings.views import import_from_dropbox
from clippings.viewsets import (DocumentViewSet,
                                SourceViewSet,
                                SourceObjectViewSet)
from main import views
from teams.views import import_teams
from teams.viewsets import TeamViewSet, PersonViewSet, PersonSeasonViewSet
from users.viewsets import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'persons', PersonViewSet)
router.register(r'teams/(?P<team_id>\d+)/documents', DocumentViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'sources', SourceViewSet)
router.register(r'issues', SourceObjectViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^import-teams/', import_teams),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^dropbox-webhook/', import_from_dropbox),
    url(r'^api/v1/', include('authentication.urls')),
    url(r'^api/v1/', include(router.urls)),

    url(r'^teams/', views.teams_view, name='teams'),
    url(r'^tournaments/', views.tournaments_view, name='tournaments'),
    url(r'^persons/', views.persons_view, name='persons'),
    url(r'^clippings/', views.clippings_view, name='clippings'),
    url(r'^$', views.main_view),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    url(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
