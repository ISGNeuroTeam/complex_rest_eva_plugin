from django.urls import re_path
from .views.example import ExampleView
from .views.hello import HelloView
from .views.timelines import TimelinesView
from .views.interesting_fields import InterestingFieldsView
from .views.dashboards import DashboardsView
from .views.dashboard import DashboardView
from .views.dashboard_export import DashboardExportView

urlpatterns = [
    re_path('example/', ExampleView.as_view()),
    re_path('hello/', HelloView.as_view()),
    re_path(r'^gettimelines/?$', TimelinesView.as_view()),
    re_path(r'^getinterestingfields/?$', InterestingFieldsView.as_view()),
    re_path(r'^dashs/?$', DashboardsView.as_view()),
    re_path(r'^dash/?$', DashboardView.as_view()),
    re_path(r'^dash/export/?$', DashboardExportView.as_view()),
    # re_path(r'^dash/import/?$', DashboardExportView.as_view()),
    # re_path(r'^dash/export/?$', DashboardExportView.as_view()),
    # re_path(r'^dash/export/?$', DashboardExportView.as_view()),
    # re_path(r'^dash/export/?$', DashboardExportView.as_view()),
    # re_path(r'^dash/export/?$', DashboardExportView.as_view()),
]