from datetime import datetime

import requests
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from library.pwd_helper import hash_password
from library.settings import API_URL


def reader_list(request):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''
        user = None

    response = requests.get(API_URL + '/users/getUsers', headers={'Authorization': token})
    readers = list(response.json())
    for reader in readers:
        reader['rentsCount'] = len(reader['rents'])

    filter_login = ''
    filter_first_name = ''
    filter_last_name = ''
    filter_rents_from = ''
    filter_rents_to = ''
    filter_date_from = ''
    filter_date_to = ''

    if request.method == 'POST':
        filter_login = request.POST['loginFilter']
        filter_first_name = request.POST['firstNameFiler']
        filter_last_name = request.POST['lastNameFiler']
        filter_rents_from = request.POST['rentsFromFilter']
        filter_rents_to = request.POST['rentsToFilter']
        filter_date_from = request.POST['dateFromFilter']
        filter_date_to = request.POST['dateToFilter']

        if filter_login != '':
            filtered_readers = list(filter(lambda r: filter_login in r['login'], readers))
            readers = filtered_readers
        if filter_first_name != '':
            filtered_readers = list(filter(lambda r: filter_first_name in r['firstName'], readers))
            readers = filtered_readers
        if filter_last_name != '':
            filtered_readers = list(filter(lambda r: filter_last_name in r['lastName'], readers))
            readers = filtered_readers
        if filter_rents_from != '':
            filtered_readers = list(filter(lambda r: r['rentsCount'] >= int(filter_rents_from), readers))
            readers = filtered_readers
        if filter_rents_to != '':
            filtered_readers = list(filter(lambda r: r['rentsCount'] <= int(filter_rents_to), readers))
            readers = filtered_readers
        if filter_date_from != '':
            filtered_readers = list(filter(
                lambda r: datetime.strptime(r['accountCreationDate'], '%Y-%m-%d') >= datetime.strptime(
                    filter_date_from, '%Y-%m-%d'), readers))
            readers = filtered_readers
        if filter_date_to != '':
            filtered_readers = list(filter(
                lambda r: datetime.strptime(r['accountCreationDate'], '%Y-%m-%d') <= datetime.strptime(
                    filter_date_to, '%Y-%m-%d'), readers))
            readers = filtered_readers

    template = loader.get_template('readers/readers.html')
    context = {
        'user': user,
        'readers': readers,
        'filterLogin': filter_login,
        'filterFirstName': filter_first_name,
        'filterLastName': filter_last_name,
        'filterRentsFrom': filter_rents_from,
        'filterRentsTo': filter_rents_to,
        'filterDateFrom': filter_date_from,
        'filterDateTo': filter_date_to
    }
    return HttpResponse(template.render(context, request))


def reader_details(request, reader_id):
    template = loader.get_template('readers/details.html')

    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        user = None
        token = ''

    response = requests.get(
        API_URL + '/users/getUser?userId=' + str(reader_id),
        headers={'Authorization': token}
    )
    reader = response.json()
    rent_count = len(reader['rents'])

    for rent in reader['rents']:
        try:
            rent_to = datetime.strptime(rent['rentFinishDate'], '%Y-%m-%d')
        except ValueError:
            rent_to = None
        except TypeError:
            rent_to = None
        rent['status'] = rent_to.date() < datetime.now().date()

    context = {
        'reader': reader,
        'user': user,
        'rentCount': rent_count
    }

    return HttpResponse(template.render(context, request))


def new_reader(request):
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
                'userRole': 'USER'
            }
            response = requests.post(
                API_URL + '/users/createUser',
                headers={'Authorization': token},
                json=body
            )
            if response.status_code == 200:
                return redirect('/readers')
            elif response.status_code == 403:
                error = 'Wybrana nazwa użytkownika jest zajęta!'
            else:
                error = 'Nieznany błąd: ' + str(response.content)

    template = loader.get_template('readers/new.html')
    context = {
        'error': error,
        'firstName': first_name,
        'user': user,
        'lastName': last_name,
        'login': login,
        'password': password
    }
    return HttpResponse(template.render(context, request))


def edit_reader(request, reader_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''
        user = None
    password = ''
    error = ''

    response = requests.get(
        API_URL + '/users/getUser?userId=' + str(reader_id),
        headers={'Authorization': token}
    )
    reader = response.json()
    first_name = reader['firstName']
    last_name = reader['lastName']

    if request.method == 'POST':
        first_name = request.POST['firstName']
        last_name = request.POST['lastName']
        password = request.POST['password']

        if first_name == '' or last_name == '':
            error = 'Musisz podać imię i nazwisko!'
        else:
            body = reader
            body['firstName'] = first_name
            body['lastName'] = last_name
            body['password'] = hash_password(password)
            response = requests.post(
                API_URL + '/users/updateUser',
                headers={'Authorization': token},
                json=body
            )
            if response.status_code == 200:
                return redirect('/readers/' + str(reader_id) + '/details')
            else:
                error = 'Nieznany błąd: ' + str(response.content)

    template = loader.get_template('readers/edit.html')
    context = {
        'error': error,
        'firstName': first_name,
        'user': user,
        'reader': reader,
        'lastName': last_name,
        'password': password
    }
    return HttpResponse(template.render(context, request))


def delete_reader(request, reader_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''

    response = requests.delete(
        API_URL + '/users/deleteUser?userId=' + str(reader_id),
        headers={'Authorization': token}
    )
    if response.status_code == 200:
        return redirect('/readers')
    else:
        print(response.content)
        return redirect('/readers/' + str(reader_id) + '/details')
