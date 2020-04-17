import requests
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader


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
            body = {'login': username, 'password': password}
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
                user['password'] = password
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


def change_password(request):
    template = loader.get_template('user/changePassword.html')
    error_message = ''
    success_message = ''
    old_password = ''
    new_password = ''
    new_password_confirmation = ''

    try:
        user = request.session['user']
    except KeyError:
        user = None

    if request.method == 'POST':
        old_password = request.POST['oldPassword']
        new_password = request.POST['newPassword']
        new_password_confirmation = request.POST['newPasswordConfirmation']

        if old_password == '' or new_password_confirmation == '' or new_password == '':
            error_message = 'Musisz wypełnić wszystkie pola!'
        elif user is None or old_password != user['password']:
            error_message = 'Nieprawidłowe hasło!'
        elif new_password != new_password_confirmation:
            error_message = 'Hasła się nie zgadzają!'
        else:
            body = {
                'accountCreationDate': user['accountCreationDate'],
                'firstName': user['firstName'],
                'id': user['id'],
                'lastName': user['lastName'],
                'login': user['login'],
                'password': new_password,
                'token': '',
                'userRole': user['userRole']
            }
            response = requests.post(
                'http://127.0.0.1:8080/users/updateUser',
                headers={'Authorization': user['token']},
                json=body
            )
            if response.status_code == 200:
                user['password'] = new_password
                request.session['user'] = user
                success_message = 'Hasło zostało zmienione.'
                error_message = ''
            elif response.status_code == 500:
                error_message = response.content

    context = {
        'errorMessage': error_message,
        'successMessage': success_message,
        'oldPassword': old_password,
        'newPassword': new_password,
        'newPasswordConfirmation': new_password_confirmation,
        'user': user
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
