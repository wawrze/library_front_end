import requests
from django.contrib.auth.models import User
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

    user = User()
    user.username = 'Ktoś'
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
