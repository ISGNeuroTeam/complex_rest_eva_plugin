from django.urls import path, include


urlpatterns = [
    path('dashboards/', include('eva_plugin.dashboards.urls')),
    path('quizs/', include('eva_plugin.quizs.urls')),
    path('themes/', include('eva_plugin.themes.urls'))
]