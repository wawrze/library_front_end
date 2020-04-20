from datetime import datetime

import requests
from django.http import HttpResponse
from django.template import loader


def reader_list(request):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''
        user = None

    response = requests.get('http://127.0.0.1:8080/users/getUsers', headers={'Authorization': token})
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
