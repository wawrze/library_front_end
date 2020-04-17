from datetime import datetime

import requests
from django.http import HttpResponse
from django.template import loader


def index(request):
    response = requests.get('http://127.0.0.1:8080/title/getTitles', headers={'Authorization': 'Bearer '})
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
        book_data = {'status': status, 'rentTo': rent_to, 'rentDays': book['rentDays']}
        books_data.append(book_data)
    title['books'] = books_data

    template = loader.get_template('catalog/books.html')
    context = {
        'title': title,
        'user': user,
        'booksCount': len(books_data)
    }
    return HttpResponse(template.render(context, request))
