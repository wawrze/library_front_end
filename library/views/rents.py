import datetime

import requests
from django.http import HttpResponse
from django.shortcuts import redirect
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
            rent_to = datetime.datetime.strptime(rent['rentFinishDate'], '%Y-%m-%d')
        except ValueError:
            rent_to = None
        except TypeError:
            rent_to = None
        rent['status'] = rent_to.date() < datetime.datetime.now().date()

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
                    lambda r: datetime.datetime.strptime(r['rentStartDate'], '%Y-%m-%d') >= datetime.datetime.strptime(
                        filter_start_date_from, '%Y-%m-%d'), rents))
                rents = filtered_rents
        except KeyError:
            filter_start_date_from = ''
        try:
            filter_start_date_to = request.POST['startDateToFilter']
            if filter_start_date_to != '':
                filtered_rents = list(filter(
                    lambda r: datetime.datetime.strptime(r['rentStartDate'], '%Y-%m-%d') <= datetime.datetime.strptime(
                        filter_start_date_to, '%Y-%m-%d'), rents))
                rents = filtered_rents
        except KeyError:
            filter_start_date_to = ''
        try:
            filter_end_date_from = request.POST['endDateFromFilter']
            if filter_end_date_from != '':
                filtered_rents = list(filter(
                    lambda r: datetime.datetime.strptime(r['rentFinishDate'], '%Y-%m-%d') >= datetime.datetime.strptime(
                        filter_end_date_from, '%Y-%m-%d'), rents))
                rents = filtered_rents
        except KeyError:
            filter_end_date_from = ''
        try:
            filter_end_date_to = request.POST['endDateToFilter']
            if filter_end_date_to != '':
                filtered_rents = list(filter(
                    lambda r: datetime.datetime.strptime(r['rentFinishDate'], '%Y-%m-%d') <= datetime.datetime.strptime(
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


def new_title_and_reader_chose(request):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        user = None
        token = ''

    response = requests.get('http://127.0.0.1:8080/title/getTitlesWithAvailableBooks')
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

    response = requests.get('http://127.0.0.1:8080/users/getUsers', headers={'Authorization': token})
    readers = list(response.json())

    try:
        login = request.GET['loginFilter']
    except KeyError:
        login = ''
    try:
        first_name = request.GET['firstNameFilter']
    except KeyError:
        first_name = ''
    try:
        last_name = request.GET['lastNameFilter']
    except KeyError:
        last_name = ''

    if login is not None and login != '':
        filtered_readers = list(filter(lambda r: login in r['login'], readers))
        readers = filtered_readers
    if first_name is not None and first_name != '':
        filtered_readers = list(filter(lambda r: first_name in r['firstName'], readers))
        readers = filtered_readers
    if last_name is not None and last_name != '':
        filtered_readers = list(filter(lambda r: last_name in r['lastName'], readers))
        readers = filtered_readers

    template = loader.get_template('rents/new.html')
    context = {
        'titles': titles,
        'readers': readers,
        'user': user,
        'author': author,
        'title': title,
        'yearFrom': year_from,
        'yearTo': year_to,
        'filterLogin': login,
        'filterFirstName': first_name,
        'filterLastName': last_name
    }
    return HttpResponse(template.render(context, request))


def new_book_and_reader_chose(request, title_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        user = None
        token = ''

    response = requests.get('http://127.0.0.1:8080/title/getTitle?titleId=' + str(title_id))
    title = response.json()
    books = title['books']
    filtered_books = list(filter(lambda b: b['rentTo'] is None or b['rentTo'] == '', books))
    title['books'] = filtered_books

    response = requests.get('http://127.0.0.1:8080/users/getUsers', headers={'Authorization': token})
    readers = list(response.json())

    try:
        login = request.GET['loginFilter']
    except KeyError:
        login = ''
    try:
        first_name = request.GET['firstNameFilter']
    except KeyError:
        first_name = ''
    try:
        last_name = request.GET['lastNameFilter']
    except KeyError:
        last_name = ''

    if login is not None and login != '':
        filtered_readers = list(filter(lambda r: login in r['login'], readers))
        readers = filtered_readers
    if first_name is not None and first_name != '':
        filtered_readers = list(filter(lambda r: first_name in r['firstName'], readers))
        readers = filtered_readers
    if last_name is not None and last_name != '':
        filtered_readers = list(filter(lambda r: last_name in r['lastName'], readers))
        readers = filtered_readers

    template = loader.get_template('rents/newTitleChosen.html')
    context = {
        'title': title,
        'readers': readers,
        'user': user,
        'filterLogin': login,
        'filterFirstName': first_name,
        'filterLastName': last_name
    }
    return HttpResponse(template.render(context, request))


def new_reader_chose(request, book_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        user = None
        token = ''

    response = requests.get('http://127.0.0.1:8080/books/getBook?bookId=' + str(book_id),
                            headers={'Authorization': token})
    book = response.json()
    rent_days = book['rentDays']
    rent_to = datetime.date.today()
    rent_to = rent_to + datetime.timedelta(days=int(rent_days))
    rent_to = rent_to.strftime("%Y-%m-%d")

    response = requests.get('http://127.0.0.1:8080/users/getUsers', headers={'Authorization': token})
    readers = list(response.json())

    try:
        login = request.GET['loginFilter']
    except KeyError:
        login = ''
    try:
        first_name = request.GET['firstNameFilter']
    except KeyError:
        first_name = ''
    try:
        last_name = request.GET['lastNameFilter']
    except KeyError:
        last_name = ''

    if login is not None and login != '':
        filtered_readers = list(filter(lambda r: login in r['login'], readers))
        readers = filtered_readers
    if first_name is not None and first_name != '':
        filtered_readers = list(filter(lambda r: first_name in r['firstName'], readers))
        readers = filtered_readers
    if last_name is not None and last_name != '':
        filtered_readers = list(filter(lambda r: last_name in r['lastName'], readers))
        readers = filtered_readers

    template = loader.get_template('rents/newBookChosen.html')
    context = {
        'book': book,
        'readers': readers,
        'user': user,
        'rentTo': rent_to,
        'filterLogin': login,
        'filterFirstName': first_name,
        'filterLastName': last_name
    }
    return HttpResponse(template.render(context, request))


def new_title_chose(request, reader_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        user = None
        token = ''

    response = requests.get('http://127.0.0.1:8080/title/getTitlesWithAvailableBooks')
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

    response = requests.get(
        'http://127.0.0.1:8080/users/getUser?userId=' + str(reader_id),
        headers={'Authorization': token}
    )
    reader = response.json()

    template = loader.get_template('rents/newReaderChosen.html')
    context = {
        'titles': titles,
        'reader': reader,
        'user': user,
        'author': author,
        'title': title,
        'yearFrom': year_from,
        'yearTo': year_to
    }
    return HttpResponse(template.render(context, request))


def new_book_chose(request, title_id, reader_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        user = None
        token = ''

    response = requests.get('http://127.0.0.1:8080/title/getTitle?titleId=' + str(title_id))
    title = response.json()
    books = title['books']
    filtered_books = list(filter(lambda b: b['rentTo'] is None or b['rentTo'] == '', books))
    title['books'] = filtered_books

    response = requests.get(
        'http://127.0.0.1:8080/users/getUser?userId=' + str(reader_id),
        headers={'Authorization': token}
    )
    reader = response.json()

    template = loader.get_template('rents/newTitleAndReaderChosen.html')
    context = {
        'title': title,
        'reader': reader,
        'user': user
    }
    return HttpResponse(template.render(context, request))


def new_summary(request, book_id, reader_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        user = None
        token = ''

    response = requests.get('http://127.0.0.1:8080/books/getBook?bookId=' + str(book_id),
                            headers={'Authorization': token})
    book = response.json()
    rent_days = book['rentDays']
    rent_to = datetime.date.today()
    rent_to = rent_to + datetime.timedelta(days=int(rent_days))
    rent_to = rent_to.strftime("%Y-%m-%d")
    response = requests.get(
        'http://127.0.0.1:8080/users/getUser?userId=' + str(reader_id),
        headers={'Authorization': token}
    )
    reader = response.json()

    template = loader.get_template('rents/newSummary.html')
    context = {
        'book': book,
        'reader': reader,
        'user': user,
        'rentTo': rent_to
    }
    return HttpResponse(template.render(context, request))


def new_confirm(request, book_id, reader_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''

    response = requests.post(
        'http://127.0.0.1:8080/rents/createRent?bookId=' + str(book_id) + '&userId=' + str(reader_id),
        headers={'Authorization': token}
    )
    if response.status_code == 200:
        return redirect('rents')
    else:
        return redirect('/rents/new/' + str(book_id) + '/' + str(reader_id) + '/summary')


def rent_details(request, rent_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        user = None
        token = ''

    response = requests.get('http://127.0.0.1:8080/rents/getRent?rentId=' + str(rent_id),
                            headers={'Authorization': token})
    rent = response.json()

    template = loader.get_template('rents/details.html')
    context = {
        'user': user,
        'rent': rent
    }
    return HttpResponse(template.render(context, request))


def book_rent_details(request, book_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''

    response = requests.get('http://127.0.0.1:8080/rents/getRentByBookId?bookId=' + str(book_id),
                            headers={'Authorization': token})
    rent = response.json()

    return redirect('/rents/' + str(rent['id']) + '/details')


def return_rent(request, rent_id):
    try:
        user = request.session['user']
        token = user['token']
    except KeyError:
        token = ''

    response = requests.delete(
        'http://127.0.0.1:8080/rents/deleteRent?rentId=' + str(rent_id),
        headers={'Authorization': token}
    )
    if response.status_code == 200:
        return redirect('/rents')
    else:
        print(response.content)
        return redirect('/rents/' + str(rent_id) + '/details')
