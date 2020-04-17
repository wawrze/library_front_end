from django.urls import path

from library.views import catalog, user

urlpatterns = [
    path('', catalog.index, name='index'),
    path('catalog', catalog.index, name='catalog'),
    path('catalog/new/', catalog.new_catalog_position, name='newCatalogPosition'),
    path('catalog/<int:position_id>/books/', catalog.books, name='positionBooks'),
    path('user/login/', user.authorize, name='login'),
    path('user/details/', user.user_details, name='userDetails'),
    path('user/logout/', user.logout, name='logout'),
]
