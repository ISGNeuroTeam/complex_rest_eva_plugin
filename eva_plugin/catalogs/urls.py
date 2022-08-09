from django.urls import re_path
from eva_plugin.catalogs.views import *

urlpatterns = [
    re_path(r'catalogs', CatalogsListHandler.as_view()),
    re_path(r'catalog', CatalogHandler.as_view()),
    re_path(r'catalog/create', CatalogHandler.as_view()),
    re_path(r'catalog/edit', CatalogHandler.as_view()),
    re_path(r'catalog/delete', CatalogHandler.as_view()),
]