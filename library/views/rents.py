from datetime import datetime

import requests
from django.http import HttpResponse
from django.template import loader


def rent_list(request):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        user = None
        token = ''

    response = requests.get('http://127.0.0.1:8080/rents/getRents', headers={'Authorization': token})
    rents = response.json()

    for rent in rents:
        try:
            rent_to = datetime.strptime(rent['rentFinishDate'], '%Y-%m-%d')
        except ValueError:
            rent_to = None
        except TypeError:
            rent_to = None
        rent['status'] = rent_to.date() < datetime.now().date()

    if request.method == 'POST':
        try:
            filter_author = request.POST['authorFilter']
            filtered_rents = list(filter(lambda r: filter_author in r['book']['title']['author'], rents))
            rents = filtered_rents
        except KeyError:
            filter_author = ''
        try:
            filter_title = request.POST['titleFilter']
            filtered_rents = list(filter(lambda r: filter_title in r['book']['title']['title'], rents))
            rents = filtered_rents
        except KeyError:
            filter_title = ''
        try:
            filter_year_from = request.POST['yearFromFilter']
            if filter_year_from != '':
                filtered_rents = list(
                    filter(lambda r: r['book']['title']['publicationYear'] >= int(filter_year_from), rents))
                rents = filtered_rents
        except KeyError:
            filter_year_from = ''
        try:
            filter_year_to = request.POST['yearToFilter']
            if filter_year_to != '':
                filtered_rents = list(
                    filter(lambda r: r['book']['title']['publicationYear'] <= int(filter_year_to), rents))
                rents = filtered_rents
        except KeyError:
            filter_year_to = ''
        try:
            filter_login = request.POST['loginFilter']
            filtered_rents = list(filter(lambda r: filter_login in r['user']['login'], rents))
            rents = filtered_rents
        except KeyError:
            filter_login = ''
        try:
            filter_first_name = request.POST['firstNameFilter']
            filtered_rents = list(filter(lambda r: filter_first_name in r['user']['firstName'], rents))
            rents = filtered_rents
        except KeyError:
            filter_first_name = ''
        try:
            filter_last_name = request.POST['lastNameFilter']
            filtered_rents = list(filter(lambda r: filter_last_name in r['user']['lastName'], rents))
            rents = filtered_rents
        except KeyError:
            filter_last_name = ''
        try:
            filter_start_date_from = request.POST['startDateFromFilter']
            if filter_start_date_from != '':
                filtered_rents = list(filter(
                    lambda r: datetime.strptime(r['rentStartDate'], '%Y-%m-%d') >= datetime.strptime(
                        filter_start_date_from, '%Y-%m-%d'), rents))
                rents = filtered_rents
        except KeyError:
            filter_start_date_from = ''
        try:
            filter_start_date_to = request.POST['startDateToFilter']
            if filter_start_date_to != '':
                filtered_rents = list(filter(
                    lambda r: datetime.strptime(r['rentStartDate'], '%Y-%m-%d') <= datetime.strptime(
                        filter_start_date_to, '%Y-%m-%d'), rents))
                rents = filtered_rents
        except KeyError:
            filter_start_date_to = ''
        try:
            filter_end_date_from = request.POST['endDateFromFilter']
            if filter_end_date_from != '':
                filtered_rents = list(filter(
                    lambda r: datetime.strptime(r['rentFinishDate'], '%Y-%m-%d') >= datetime.strptime(
                        filter_end_date_from, '%Y-%m-%d'), rents))
                rents = filtered_rents
        except KeyError:
            filter_end_date_from = ''
        try:
            filter_end_date_to = request.POST['endDateToFilter']
            if filter_end_date_to != '':
                filtered_rents = list(filter(
                    lambda r: datetime.strptime(r['rentFinishDate'], '%Y-%m-%d') <= datetime.strptime(
                        filter_end_date_to, '%Y-%m-%d'), rents))
                rents = filtered_rents
        except KeyError:
            filter_end_date_to = ''
    else:
        filter_author = ''
        filter_title = ''
        filter_year_from = ''
        filter_year_to = ''
        filter_login = ''
        filter_first_name = ''
        filter_last_name = ''
        filter_start_date_from = ''
        filter_start_date_to = ''
        filter_end_date_from = ''
        filter_end_date_to = ''

    template = loader.get_template('rents/rents.html')
    context = {
        'user': user,
        'rents': rents,
        'filterAuthor': filter_author,
        'filterTitle': filter_title,
        'filterYearFrom': filter_year_from,
        'filterYearTo': filter_year_to,
        'filterLogin': filter_login,
        'filterFirstName': filter_first_name,
        'filterLastName': filter_last_name,
        'filterStartDateFrom': filter_start_date_from,
        'filterStartDateTo': filter_start_date_to,
        'filterEndDateFrom': filter_end_date_from,
        'filterEndDateTo': filter_end_date_to
    }

    return HttpResponse(template.render(context, request))
