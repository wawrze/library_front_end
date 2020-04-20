from datetime import datetime

import requests
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader


def index(request):
    response = requests.get('http://127.0.0.1:8080/title/getTitles')
    titles = list(response.json())

    try:
        author = request.GET['author']
    except KeyError:
        author = ''
    try:
        title = request.GET['title']
    except KeyError:
        title = ''
    try:
        year_from = request.GET['year_from']
    except KeyError:
        year_from = ''
    try:
        year_to = request.GET['year_to']
    except KeyError:
        year_to = ''

    if author is not None and author != '':
        filtered_titles = list(filter(lambda t: author in t['author'], titles))
        titles = filtered_titles
    if title is not None and title != '':
        filtered_titles = list(filter(lambda t: title in t['title'], titles))
        titles = filtered_titles
    if year_from is not None and year_from != '':
        filtered_titles = list(filter(lambda t: t['publicationYear'] >= int(year_from), titles))
        titles = filtered_titles
    if year_to is not None and year_to != '':
        filtered_titles = list(filter(lambda t: t['publicationYear'] <= int(year_to), titles))
        titles = filtered_titles

    try:
        user = request.session['user']
    except KeyError:
        user = None

    template = loader.get_template('catalog/index.html')
    context = {
        'titles': titles,
        'user': user,
        'author': author,
        'title': title,
        'yearFrom': year_from,
        'yearTo': year_to
    }
    return HttpResponse(template.render(context, request))


def books(request, position_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''
        user = None

    response = requests.get(
        'http://127.0.0.1:8080/title/getTitle?titleId=' + str(position_id),
        headers={'Authorization': token}
    )
    title = response.json()

    title_books = title['books']
    now = datetime.now()
    books_data = []
    for book in title_books:
        try:
            rent_to = datetime.strptime(book['rentTo'], '%Y-%m-%d')
        except ValueError:
            rent_to = None
        except TypeError:
            rent_to = None

        if rent_to is None:
            status = 0
        elif rent_to.date() > now.date():
            status = 1
        else:
            status = 2
        if rent_to is None:
            rent_to = '-'
        else:
            rent_to = book['rentTo']
        book_data = {'id': book['id'], 'status': status, 'rentTo': rent_to, 'rentDays': book['rentDays']}
        books_data.append(book_data)
    title['books'] = books_data

    template = loader.get_template('catalog/books.html')
    context = {
        'title': title,
        'user': user,
        'booksCount': len(books_data)
    }
    return HttpResponse(template.render(context, request))


def new_catalog_position(request):
    author = ''
    title = ''
    publication_year = ''
    error = ''

    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''
        user = None

    if request.method == 'POST':
        author = request.POST['author']
        title = request.POST['title']
        publication_year = request.POST['publicationYear']

        if author == '' or title == '' or publication_year == '':
            error = "Musisz wypełnić wszystkie pola!"
        else:
            body = {'author': author, 'title': title, 'publicationYear': publication_year}
            response = requests.post(
                'http://127.0.0.1:8080/title/createTitle',
                headers={'Authorization': token},
                json=body
            )
            if response.status_code == 200:
                return redirect('catalog')
            else:
                error = 'Nieznany błąd: ' + str(response.content)

    template = loader.get_template('catalog/new.html')
    context = {
        'error': error,
        'title': title,
        'user': user,
        'author': author,
        'publicationYear': publication_year
    }
    return HttpResponse(template.render(context, request))


def edit_catalog_position(request, position_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''
        user = None

    response = requests.get(
        'http://127.0.0.1:8080/title/getTitle?titleId=' + str(position_id),
        headers={'Authorization': token}
    )
    position = response.json()
    author = position['author']
    title = position['title']
    publication_year = position['publicationYear']
    error = ''

    if request.method == 'POST':
        author = request.POST['author']
        title = request.POST['title']
        publication_year = request.POST['publicationYear']

        if author == '' or title == '' or publication_year == '':
            error = "Musisz wypełnić wszystkie pola!"
        else:
            body = {'id': position_id, 'author': author, 'title': title, 'publicationYear': publication_year}
            response = requests.post(
                'http://127.0.0.1:8080/title/updateTitle',
                headers={'Authorization': token},
                json=body
            )
            if response.status_code == 200:
                return redirect('/catalog/' + str(position_id) + '/books')
            else:
                error = 'Nieznany błąd: ' + str(response.content)

    template = loader.get_template('catalog/edit.html')
    context = {
        'error': error,
        'title': title,
        'user': user,
        'author': author,
        'publicationYear': publication_year
    }
    return HttpResponse(template.render(context, request))


def new_book(request, position_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''
        user = None

    response = requests.get(
        'http://127.0.0.1:8080/title/getTitle?titleId=' + str(position_id),
        headers={'Authorization': token}
    )
    title = response.json()
    rent_days = ''
    error = ''

    if request.method == 'POST':
        rent_days = request.POST['rentDays']
        if rent_days is None or rent_days == '':
            error = 'Musisz podać liczbę dni!'
        else:
            body = {'rentDays': rent_days, 'title': title}
            response = requests.post(
                'http://127.0.0.1:8080/books/createBook',
                headers={'Authorization': token},
                json=body
            )
            if response.status_code == 200:
                return redirect('/catalog/' + str(position_id) + '/books')
            else:
                error = 'Nieznany błąd: ' + str(response.content)

    template = loader.get_template('catalog/newBook.html')
    context = {
        'error': error,
        'title': title,
        'user': user,
        'rentDays': rent_days
    }
    return HttpResponse(template.render(context, request))


def edit_book(request, position_id, book_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''
        user = None

    response = requests.get(
        'http://127.0.0.1:8080/books/getBook?bookId=' + str(book_id),
        headers={'Authorization': token}
    )
    book = response.json()
    rent_days = book['rentDays']
    try:
        rent_to = datetime.strptime(book['rentTo'], '%Y-%m-%d')
    except ValueError:
        rent_to = None
    except TypeError:
        rent_to = None

    if rent_to is None:
        status = 'Dostępna'
    elif rent_to.date() > datetime.now().date():
        status = 'Niedostępna'
    else:
        status = 'Wypożyczenie przeterminowane'
    if rent_to is None:
        rent_to = '-'
    else:
        rent_to = book['rentTo']
    error = ''

    if request.method == 'POST':
        rent_days = request.POST['rentDays']
        if rent_days is None or rent_days == '':
            error = 'Musisz podać liczbę dni!'
        else:
            body = book
            body['rentDays'] = rent_days
            response = requests.post(
                'http://127.0.0.1:8080/books/updateBook',
                headers={'Authorization': token},
                json=body
            )
            if response.status_code == 200:
                return redirect('/catalog/' + str(position_id) + '/books')
            else:
                error = 'Nieznany błąd: ' + str(response.content)

    template = loader.get_template('catalog/editBook.html')
    context = {
        'error': error,
        'book': book,
        'user': user,
        'status': status,
        'rentTo': rent_to,
        'rentDays': rent_days
    }
    return HttpResponse(template.render(context, request))


def delete_catalog_position(request, position_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''

    response = requests.delete(
        'http://127.0.0.1:8080/title/deleteTitle?titleId=' + str(position_id),
        headers={'Authorization': token}
    )
    if response.status_code == 200:
        return redirect('/catalog')
    else:
        print(response.content)
        return redirect('/catalog/' + str(position_id) + '/books')


def delete_book(request, position_id, book_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''

    response = requests.delete(
        'http://127.0.0.1:8080/books/deleteBook?bookId=' + str(book_id),
        headers={'Authorization': token}
    )
    if response.status_code == 200:
        return redirect('/catalog/' + str(position_id) + '/books')
    else:
        print(response.content)
        return redirect('/catalog/' + str(position_id) + '/books/' + str(book_id) + '/edit')
