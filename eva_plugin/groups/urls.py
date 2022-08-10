from django.urls import re_path
from eva_plugin.groups.views import GroupsHandler, GroupHandler, GroupDashboardsHandler, UserGroupsHandler
from eva_plugin.dashs.views import GroupExportHandler, GroupImportHandler


urlpatterns = [
    re_path(r'^groups/?$', GroupsHandler.as_view()),
    re_path(r'^group/?$', GroupHandler.as_view()),
    re_path(r'^group/export/?$', GroupExportHandler.as_view()),
    re_path(r'^group/import/?$', GroupImportHandler.as_view()),
    re_path(r'^group/dashs/?$', GroupDashboardsHandler.as_view()),
    re_path(r'^user/groups/?$', UserGroupsHandler.as_view())
]
