from django.urls import re_path
from cache import cache_page
from .views.themes import *

# Use cache_page decorator for caching view

# urlpatterns = [
#     path('example/', cache_page(60 * 15)(ExampleView.as_view())),
# ]

urlpatterns = [
    re_path(r'^themes/?$', ThemeListView.as_view()),
    re_path(r'^theme/?$', ThemeGetView.as_view()),
    re_path(r'^theme/create/?$', ThemeCreateView.as_view()),
    re_path(r'^theme/delete/?$', ThemeDeleteView.as_view()),
]
