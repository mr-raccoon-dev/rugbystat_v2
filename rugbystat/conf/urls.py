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
from matches.views import (import_seasons, SeasonCreateView,
                           TournamentListView, TournamentDetailView,
                           TournamentAutocomplete, SeasonAutocomplete)
from teams.views import (import_teams,
                         PersonCreateView, PersonUpdateView, TeamUpdateView,
                         TeamAutocomplete)
from teams.viewsets import TeamViewSet, PersonViewSet, PersonSeasonViewSet
from users.viewsets import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'persons', PersonViewSet)
router.register(r'personseasons', PersonSeasonViewSet)
router.register(r'teams/(?P<team_id>\d+)/documents', DocumentViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'sources', SourceViewSet)
router.register(r'issues', SourceObjectViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/', include('authentication.urls')),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^markdownx/', include('markdownx.urls')),
    url(r'^import-teams/', import_teams),
    url(r'^import-seasons/', import_seasons, name='import_seasons'),
    url(r'^dropbox-webhook/', import_from_dropbox),

    url(r'^autocomplete-tournaments/$', TournamentAutocomplete.as_view(),
        name='autocomplete-tournaments'),
    url(r'^autocomplete-seasons/$', SeasonAutocomplete.as_view(),
        name='autocomplete-seasons'),
    url(r'^autocomplete-teams/$', TeamAutocomplete.as_view(),
        name='autocomplete-teams'),

    url(r'^teams/$', views.teams_view, name='teams'),
    url(r'^teams/(?P<pk>\d+)/', TeamUpdateView.as_view(), name='teams_detail'),
    url(r'^tournaments/$', TournamentListView.as_view(), name='tournaments'),
    url(r'^tournaments/(?P<pk>\d+)/', TournamentDetailView.as_view(),
        name='tournament_detail'),
    url(r'^seasons/new/', SeasonCreateView.as_view(), name='seasons_new'),
    url(r'^persons/$', views.persons_view, name='persons'),
    url(r'^persons/(?P<pk>\d+)/', PersonUpdateView.as_view(),
        name='persons_detail'),
    url(r'^persons/new/', PersonCreateView.as_view(), name='persons_new'),

    url(r'^clippings/', views.clippings_view, name='clippings'),
    url(r'^$', views.main_view),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    url(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'),
        permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
