from django.urls import re_path

from eva_plugin.auth.views.login import AuthLoginHandler

from eva_plugin.auth.views.role_model import UsersHandler, UserHandler, RoleHandler, RolesHandler, \
    UserPermissionsHandler, UserSettingHandler, PermissionsHandler, PermissionHandler


urlpatterns = [

    re_path(r'^auth/login/?$', AuthLoginHandler.as_view()),
    re_path(r'^users/?$', UsersHandler.as_view()),
    re_path(r'^user/?$', UserHandler.as_view()),
    re_path(r'^user/roles/?$', RolesHandler.as_view()),
    re_path(r'^user/permissions/?$', UserPermissionsHandler.as_view()),
    re_path(r'^user/users/?$', UsersHandler.as_view()),
    re_path(r'^user/setting/?$', UserSettingHandler.as_view()),
    re_path(r'^roles/?$', RolesHandler.as_view()),
    re_path(r'^role/?$', RoleHandler.as_view()),
    re_path(r'^permissions/?$', PermissionsHandler.as_view()),
    re_path(r'^permission/?$', PermissionHandler.as_view()),
]