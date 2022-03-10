from rest.urls import path
from cache import cache_page
from .views.example import ExampleView
from .views.hello import HelloView
from .views.themes import *

# Use cache_page decorator for caching view

# urlpatterns = [
#     path('example/', cache_page(60 * 15)(ExampleView.as_view())),
# ]

urlpatterns = [
    path('example/', ExampleView.as_view()),
    path('hello/', HelloView.as_view()),
    path('themes/', ThemeListView.as_view()),
    path('theme/', ThemeGetView.as_view()),
    path('theme/create', ThemeCreateView.as_view()),
    path('theme/delete', ThemeDeleteView.as_view()),
]