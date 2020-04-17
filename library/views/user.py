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
