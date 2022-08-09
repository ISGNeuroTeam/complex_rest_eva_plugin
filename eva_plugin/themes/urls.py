from django.urls import re_path
from eva_plugin.themes.views import *


urlpatterns = [
    re_path(r'^themes/?$', ThemeListHandler.as_view()),
    re_path(r'^theme/?$', ThemeGetHandler.as_view()),
    re_path(r'^theme/create/?$', ThemeHandler.as_view()),
    re_path(r'^theme/delete/?$', ThemeHandler.as_view()),
]
