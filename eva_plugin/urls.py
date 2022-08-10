from django.urls import re_path

from eva_plugin.auth.urls import urlpatterns as auth_urlpatterns
from eva_plugin.dashs.urls import urlpatterns as dash_urlpatterns
from eva_plugin.groups.urls import urlpatterns as group_urlpatterns
from eva_plugin.catalogs.urls import urlpatterns as catalog_urlpatterns
from eva_plugin.themes.urls import urlpatterns as theme_urlpatterns
from eva_plugin.indexes.urls import urlpatterns as index_urlpatterns


from eva_plugin.interesting_fields.views import InterestingFieldsView
from eva_plugin.timelines.views import TimelinesView
from eva_plugin.logs.views import LogsHandler
from eva_plugin.svg.views import SvgLoadHandler


urlpatterns = [
    re_path(r'^getinterestingfields/?$', InterestingFieldsView.as_view()),
    re_path(r'^gettimelines/?$', TimelinesView.as_view()),
    re_path(r'^logs/save/?$', LogsHandler.as_view()),
    re_path(r'^load/svg/?$', SvgLoadHandler.as_view()),

] + auth_urlpatterns + dash_urlpatterns + group_urlpatterns + catalog_urlpatterns + theme_urlpatterns\
              + index_urlpatterns
