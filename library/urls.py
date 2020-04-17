from django.urls import path

from library.views import catalog, user

urlpatterns = [
    path('', catalog.index, name='index'),
    path('login/', user.authorize, name='login'),
]
