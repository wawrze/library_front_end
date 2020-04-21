from datetime import datetime

import requests
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from library.pwd_helper import hash_password
from library.settings import API_URL


def admin_list(request):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''
        user = None

    response = requests.get(API_URL + '/users/getAdmins', headers={'Authorization': token})
    admins = list(response.json())

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
            filtered_readers = list(filter(lambda r: filter_login in r['login'], admins))
            admins = filtered_readers
        if filter_first_name != '':
            filtered_readers = list(filter(lambda r: filter_first_name in r['firstName'], admins))
            admins = filtered_readers
        if filter_last_name != '':
            filtered_readers = list(filter(lambda r: filter_last_name in r['lastName'], admins))
            admins = filtered_readers
        if filter_date_from != '':
            filtered_readers = list(filter(
                lambda r: datetime.strptime(r['accountCreationDate'], '%Y-%m-%d') >= datetime.strptime(
                    filter_date_from, '%Y-%m-%d'), admins))
            admins = filtered_readers
        if filter_date_to != '':
            filtered_readers = list(filter(
                lambda r: datetime.strptime(r['accountCreationDate'], '%Y-%m-%d') <= datetime.strptime(
                    filter_date_to, '%Y-%m-%d'), admins))
            admins = filtered_readers

    template = loader.get_template('admins/admins.html')
    context = {
        'user': user,
        'admins': admins,
        'filterLogin': filter_login,
        'filterFirstName': filter_first_name,
        'filterLastName': filter_last_name,
        'filterDateFrom': filter_date_from,
        'filterDateTo': filter_date_to
    }
    return HttpResponse(template.render(context, request))


def admin_details(request, admin_id):
    template = loader.get_template('admins/details.html')

    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        user = None
        token = ''

    response = requests.get(
        API_URL + '/users/getUser?userId=' + str(admin_id),
        headers={'Authorization': token}
    )
    admin = response.json()

    context = {
        'admin': admin,
        'user': user
    }

    return HttpResponse(template.render(context, request))


def new_admin(request):
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
                'userRole': 'ADMIN'
            }
            response = requests.post(
                API_URL + '/users/createUser',
                headers={'Authorization': token},
                json=body
            )
            if response.status_code == 200:
                return redirect('/admins')
            elif response.status_code == 403:
                error = 'Wybrana nazwa użytkownika jest zajęta!'
            else:
                error = 'Nieznany błąd: ' + str(response.content)

    template = loader.get_template('admins/new.html')
    context = {
        'error': error,
        'firstName': first_name,
        'user': user,
        'lastName': last_name,
        'login': login,
        'password': password
    }
    return HttpResponse(template.render(context, request))


def edit_admin(request, admin_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''
        user = None
    password = ''
    error = ''

    response = requests.get(
        API_URL + '/users/getUser?userId=' + str(admin_id),
        headers={'Authorization': token}
    )
    admin = response.json()
    first_name = admin['firstName']
    last_name = admin['lastName']

    if request.method == 'POST':
        first_name = request.POST['firstName']
        last_name = request.POST['lastName']
        password = request.POST['password']

        if first_name == '' or last_name == '':
            error = 'Musisz podać imię i nazwisko!'
        else:
            body = admin
            body['firstName'] = first_name
            body['lastName'] = last_name
            body['password'] = hash_password(password)
            response = requests.post(
                API_URL + '/users/updateUser',
                headers={'Authorization': token},
                json=body
            )
            if response.status_code == 200:
                return redirect('/admins/' + str(admin_id) + '/details')
            else:
                error = 'Nieznany błąd: ' + str(response.content)

    template = loader.get_template('admins/edit.html')
    context = {
        'error': error,
        'firstName': first_name,
        'user': user,
        'admin': admin,
        'lastName': last_name,
        'password': password
    }
    return HttpResponse(template.render(context, request))


def delete_admin(request, admin_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''

    response = requests.delete(
        API_URL + '/users/deleteUser?userId=' + str(admin_id),
        headers={'Authorization': token}
    )
    if response.status_code == 200:
        return redirect('/admins')
    else:
        print(response.content)
        return redirect('/admins/' + str(admin_id) + '/details')
