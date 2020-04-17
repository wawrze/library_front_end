from django.urls import path

from library.views import catalog, user

urlpatterns = [
    path('', catalog.index, name='index'),
    path('user/login/', user.authorize, name='login'),
    path('user/changePassword/', user.change_password, name='changePassword'),
    path('user/logout/', user.logout, name='logout'),
]
