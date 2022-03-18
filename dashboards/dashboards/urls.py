from django.urls import re_path
from .views.hello import HelloView
from .views.timelines import TimelinesView
from .views.interesting_fields import InterestingFieldsView
from .views.dashboards import DashboardsView
from .views.dashboard import DashboardView
from .views.dashboard_export import DashboardExportView
from .views.dashboard_import import DashboardImportView
from .views.logs import LogsView
from .views.svg_load import SvgLoadView
from .views.group_dashboards import GroupDashboardsView
from .views.group_export import GroupExportView
from .views.group_import import GroupImportView
from .views.dash_by_name import DashByNameView

urlpatterns = [
    re_path('hello/', HelloView.as_view()),
    re_path(r'^gettimelines/?$', TimelinesView.as_view()),
    re_path(r'^getinterestingfields/?$', InterestingFieldsView.as_view()),
    re_path(r'^dashs/?$', DashboardsView.as_view()),
    re_path(r'^dash/?$', DashboardView.as_view()),
    re_path(r'^dash/export/?$', DashboardExportView.as_view()),
    re_path(r'^dash/import/?$', DashboardImportView.as_view()),
    re_path(r'^dashByName/?$', DashByNameView.as_view()),
    re_path(r'^load/svg/?$', SvgLoadView.as_view()),
    re_path(r'^group/export/?$', GroupExportView.as_view()),
    re_path(r'^group/import/?$', GroupImportView.as_view()),
    re_path(r'^group/dashs/?$', GroupDashboardsView.as_view()),
    re_path(r'^logs/save/?$', LogsView.as_view()),
]