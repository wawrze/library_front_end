from django.urls import path

from library.views import catalog, user, readers

urlpatterns = [
    path('', catalog.index, name='index'),
    path('catalog', catalog.index, name='catalog'),
    path('catalog/new/', catalog.new_catalog_position, name='newCatalogPosition'),
    path('catalog/<int:position_id>/edit/', catalog.edit_catalog_position, name='editCatalogPosition'),
    path('catalog/<int:position_id>/delete/', catalog.delete_catalog_position, name='deleteCatalogPosition'),
    path('catalog/<int:position_id>/books/', catalog.books, name='positionBooks'),
    path('catalog/<int:position_id>/books/new/', catalog.new_book, name='newBook'),
    path('catalog/<int:position_id>/books/<int:book_id>/edit', catalog.edit_book, name='editBook'),
    path('catalog/<int:position_id>/books/<int:book_id>/delete', catalog.delete_book, name='deleteBook'),
    path('user/login/', user.authorize, name='login'),
    path('user/details/', user.user_details, name='userDetails'),
    path('user/logout/', user.logout, name='logout'),
    path('readers', readers.reader_list, name='readers'),
    path('readers/new', readers.new_reader, name='newReader'),
    path('readers/<int:reader_id>/details', readers.reader_details, name='readerDetails'),
    path('readers/<int:reader_id>/edit', readers.edit_reader, name='editReader'),
    path('readers/<int:reader_id>/delete', readers.delete_reader, name='deleteReader'),
]
