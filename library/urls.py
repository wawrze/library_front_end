from django.urls import path

from library.views import catalog

urlpatterns = [
    path('', catalog.index, name='index'),
]
