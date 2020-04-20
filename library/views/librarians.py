from datetime import datetime

import requests
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from library.pwd_helper import hash_password


def librarian_list(request):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''
        user = None

    response = requests.get('http://127.0.0.1:8080/users/getLibrarians', headers={'Authorization': token})
    librarians = list(response.json())
    for reader in librarians:
        reader['rentsCount'] = len(reader['rents'])

    filter_login = ''
    filter_first_name = ''
    filter_last_name = ''
    filter_date_from = ''
    filter_date_to = ''

    if request.method == 'POST':
        filter_login = request.POST['loginFilter']
        filter_first_name = request.POST['firstNameFiler']
        filter_last_name = request.POST['lastNameFiler']
        filter_date_from = request.POST['dateFromFilter']
        filter_date_to = request.POST['dateToFilter']

        if filter_login != '':
            filtered_readers = list(filter(lambda r: filter_login in r['login'], librarians))
            librarians = filtered_readers
        if filter_first_name != '':
            filtered_readers = list(filter(lambda r: filter_first_name in r['firstName'], librarians))
            librarians = filtered_readers
        if filter_last_name != '':
            filtered_readers = list(filter(lambda r: filter_last_name in r['lastName'], librarians))
            librarians = filtered_readers
        if filter_date_from != '':
            filtered_readers = list(filter(
                lambda r: datetime.strptime(r['accountCreationDate'], '%Y-%m-%d') >= datetime.strptime(
                    filter_date_from, '%Y-%m-%d'), librarians))
            librarians = filtered_readers
        if filter_date_to != '':
            filtered_readers = list(filter(
                lambda r: datetime.strptime(r['accountCreationDate'], '%Y-%m-%d') <= datetime.strptime(
                    filter_date_to, '%Y-%m-%d'), librarians))
            librarians = filtered_readers

    template = loader.get_template('librarians/librarians.html')
    context = {
        'user': user,
        'librarians': librarians,
        'filterLogin': filter_login,
        'filterFirstName': filter_first_name,
        'filterLastName': filter_last_name,
        'filterDateFrom': filter_date_from,
        'filterDateTo': filter_date_to
    }
    return HttpResponse(template.render(context, request))


def librarian_details(request, librarian_id):
    template = loader.get_template('librarians/details.html')

    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        user = None
        token = ''

    response = requests.get(
        'http://127.0.0.1:8080/users/getUser?userId=' + str(librarian_id),
        headers={'Authorization': token}
    )
    librarian = response.json()

    context = {
        'librarian': librarian,
        'user': user
    }

    return HttpResponse(template.render(context, request))


def new_librarian(request):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''
        user = None
    first_name = ''
    last_name = ''
    login = ''
    password = ''
    error = ''

    if request.method == 'POST':
        first_name = request.POST['firstName']
        last_name = request.POST['lastName']
        login = request.POST['login']
        password = request.POST['password']

        if first_name == '' or last_name == '' or login == '' or password == '':
            error = 'Musisz wypełnić wszystkie pola!'
        else:
            body = {
                'firstName': first_name,
                'lastName': last_name,
                'login': login,
                'password': hash_password(password),
                'userRole': 'LIBRARIAN'
            }
            response = requests.post(
                'http://127.0.0.1:8080/users/createUser',
                headers={'Authorization': token},
                json=body
            )
            if response.status_code == 200:
                return redirect('/librarians')
            elif response.status_code == 403:
                error = 'Wybrana nazwa użytkownika jest zajęta!'
            else:
                error = 'Nieznany błąd: ' + str(response.content)

    template = loader.get_template('librarians/new.html')
    context = {
        'error': error,
        'firstName': first_name,
        'user': user,
        'lastName': last_name,
        'login': login,
        'password': password
    }
    return HttpResponse(template.render(context, request))


def edit_librarian(request, librarian_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''
        user = None
    password = ''
    error = ''

    response = requests.get(
        'http://127.0.0.1:8080/users/getUser?userId=' + str(librarian_id),
        headers={'Authorization': token}
    )
    librarian = response.json()
    first_name = librarian['firstName']
    last_name = librarian['lastName']

    if request.method == 'POST':
        first_name = request.POST['firstName']
        last_name = request.POST['lastName']
        password = request.POST['password']

        if first_name == '' or last_name == '':
            error = 'Musisz podać imię i nazwisko!'
        else:
            body = librarian
            body['firstName'] = first_name
            body['lastName'] = last_name
            body['password'] = hash_password(password)
            response = requests.post(
                'http://127.0.0.1:8080/users/updateUser',
                headers={'Authorization': token},
                json=body
            )
            if response.status_code == 200:
                return redirect('/librarians/' + str(librarian_id) + '/details')
            else:
                error = 'Nieznany błąd: ' + str(response.content)

    template = loader.get_template('librarians/edit.html')
    context = {
        'error': error,
        'firstName': first_name,
        'user': user,
        'librarian': librarian,
        'lastName': last_name,
        'password': password
    }
    return HttpResponse(template.render(context, request))


def delete_librarian(request, librarian_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''

    response = requests.delete(
        'http://127.0.0.1:8080/users/deleteUser?userId=' + str(librarian_id),
        headers={'Authorization': token}
    )
    if response.status_code == 200:
        return redirect('/librarians')
    else:
        print(response.content)
        return redirect('/librarians/' + str(librarian_id) + '/details')
