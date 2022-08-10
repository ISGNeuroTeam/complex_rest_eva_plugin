from django.urls import re_path
from .views import DashImportHandler, DashExportHandler, DashboardHandler, DashboardsHandler, DashByNameHandler, UserDashboardsHandler

urlpatterns = [
    re_path(r'^dashs/?$', DashboardsHandler.as_view()),
    re_path(r'^dash/?$', DashboardHandler.as_view()),
    re_path(r'^dash/export/?$', DashExportHandler.as_view()),
    re_path(r'^dash/import/?$', DashImportHandler.as_view()),
    re_path(r'^dashByName/?$', DashByNameHandler.as_view()),
    re_path(r'^user/dashs/?$', UserDashboardsHandler.as_view()),
]
