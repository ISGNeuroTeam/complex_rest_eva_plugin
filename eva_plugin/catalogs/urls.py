from django.urls import re_path
from eva_plugin.catalogs.views import *

urlpatterns = [
    re_path(r'^qapi/catalogs/?$', CatalogsListHandler.as_view()),
    re_path(r'^qapi/catalog/?$', CatalogHandler.as_view()),
    re_path(r'^qapi/catalog/create/?$', CatalogHandler.as_view()),
    re_path(r'^qapi/catalog/edit/?$', CatalogHandler.as_view()),
    re_path(r'^qapi/catalog/delete/?$', CatalogHandler.as_view()),
]