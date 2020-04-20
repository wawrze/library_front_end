from django.urls import path

from library.views import catalog, user, readers, librarians, admins, rents

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
    path('librarians', librarians.librarian_list, name='librarians'),
    path('librarians/new', librarians.new_librarian, name='newLibrarian'),
    path('librarians/<int:librarian_id>/details', librarians.librarian_details, name='librarianDetails'),
    path('librarians/<int:librarian_id>/edit', librarians.edit_librarian, name='editLibrarian'),
    path('librarians/<int:librarian_id>/delete', librarians.delete_librarian, name='deleteLibrarian'),
    path('admins', admins.admin_list, name='admins'),
    path('admins/new', admins.new_admin, name='newAdmin'),
    path('admins/<int:admin_id>/details', admins.admin_details, name='adminDetails'),
    path('admins/<int:admin_id>/edit', admins.edit_admin, name='editAdmin'),
    path('admins/<int:admin_id>/delete', admins.delete_admin, name='deleteAdmin'),
    path('rents', rents.rent_list, name='rents')
]
