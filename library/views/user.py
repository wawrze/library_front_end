from datetime import datetime

import requests
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from library.pwd_helper import hash_password


def authorize(request):
    template = loader.get_template('user/login.html')
    error = ''
    username = ''
    password = ''

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if username is None or username == '':
            error = 'Musisz podać nazwę użytkownika!'
        elif password is None or password == '':
            error = 'Musisz podać hasło!'
        else:
            body = {'login': username, 'password': hash_password(password)}
            response = requests.post('http://127.0.0.1:8080/account/login', json=body)
            user = response.json()
            try:
                status = user['status']
            except KeyError:
                status = 200
            if status == 403:
                if user['message'] == 'No user!':
                    error = 'Nieprawidłowy login!'
                elif user['message'] == 'Wrong password!':
                    error = 'Nieprawidłowe hasło!'
                else:
                    error = 'Błąd logowania! Wprowadź dane i spróbuj ponownie.'
                    username = ''
                    password = ''
            elif status != 200:
                error = 'Błąd logowania! Wprowadź dane i spróbuj ponownie.'
                username = ''
                password = ''
            else:
                user['password'] = hash_password(password)
                token = 'Bearer ' + user['token']
                user['token'] = token
                request.session.clear()
                request.session['user'] = user
                return redirect('/')

    context = {
        'error': error,
        'username': username,
        'password': password,
        'user': None
    }

    return HttpResponse(template.render(context, request))


def user_details(request):
    template = loader.get_template('user/userDetails.html')
    error_message = ''
    success_message = ''
    old_password = ''
    new_password = ''
    new_password_confirmation = ''

    try:
        user = request.session['user']
        response = requests.get(
            'http://127.0.0.1:8080/users/getUser?userId=' + str(user['id']),
            headers={'Authorization': user['token']}
        )
        response_user = response.json()
        for rent in response_user['rents']:
            try:
                rent_to = datetime.strptime(rent['rentFinishDate'], '%Y-%m-%d')
            except ValueError:
                rent_to = None
            except TypeError:
                rent_to = None
            rent['status'] = rent_to.date() < datetime.now().date()
    except KeyError:
        user = None
        response_user = None

    if request.method == 'POST':
        old_password = request.POST['oldPassword']
        new_password = request.POST['newPassword']
        new_password_confirmation = request.POST['newPasswordConfirmation']

        if old_password == '' or new_password_confirmation == '' or new_password == '':
            error_message = 'Musisz wypełnić wszystkie pola!'
        elif user is None or hash_password(old_password) != user['password']:
            error_message = 'Nieprawidłowe hasło!'
        elif new_password != new_password_confirmation:
            error_message = 'Hasła się nie zgadzają!'
        else:
            body = {
                'accountCreationDate': response_user['accountCreationDate'],
                'firstName': response_user['firstName'],
                'id': response_user['id'],
                'lastName': response_user['lastName'],
                'login': response_user['login'],
                'password': hash_password(new_password),
                'token': '',
                'userRole': response_user['userRole']
            }
            response = requests.post(
                'http://127.0.0.1:8080/users/updateUser',
                headers={'Authorization': response_user['token']},
                json=body
            )
            if response.status_code == 200:
                response_user['password'] = hash_password(new_password)
                request.session['user'] = response_user
                success_message = 'Hasło zostało zmienione.'
                error_message = ''
                old_password = ''
                new_password = ''
                new_password_confirmation = ''
            elif response.status_code == 500:
                error_message = 'Nieznany błąd: ' + str(response.content)

    context = {
        'errorMessage': error_message,
        'successMessage': success_message,
        'oldPassword': old_password,
        'newPassword': new_password,
        'newPasswordConfirmation': new_password_confirmation,
        'user': response_user
    }

    return HttpResponse(template.render(context, request))


def logout(request):
    try:
        user = request.session['user']
        requests.delete(
            'http://127.0.0.1:8080/account/logout',
            headers={'Authorization': user['token']}
        )
    finally:
        request.session.clear()
        return redirect('/')
