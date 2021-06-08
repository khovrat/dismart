import json
import math
import requests
import datetime
import pandas as pd
import numpy as np
from decouple import config
from django.core import serializers
from django.utils.translation import get_language



def set_init_variables(request):
    context = {
        'links': {
            'instagram': config("INSTAGRAM_URL"),
            'twitter': config("TWITTER_URL"),
            'facebook': config("FACEBOOK_URL"),
            'github': config("GITHUB_URL"),
            'google': config("GOOGLE_URL"),
            'admin_panel': config("SERVER_URL"),
            'my_facebook': config("MY_FACEBOOK"),
            'my_twitter': config("MY_TWITTER"),
            'my_linkedin': config("MY_LINKEDIN"),
            'video': get_video_links(get_language())
        }
    }
    request.session['status_code'] = 0
    return context


def get_video_links(language):
    if language == 'en':
        return 'C8oU0NASU3I'
    if language == 'uk':
        return 'HkOazyU61Ys'
    if language == 'ru':
        return 'XA7Lhk25abE'
    if language == 'de':
        return 'Mcmco-8f_xM'
    if language == 'be':
        return 'frrj1MpmEME'


def set_amount_info():
    response = requests.get(config("SERVER_URL") + "/api/amount-info/")
    data = json.loads(response.text)
    if response.status_code == 200:
        return {
            'amount': {
                'users': data['users'],
                'companies': data['companies'],
                'articles': data['articles'],
                'advices': data['advices']
            }
        }
    return dict()


def set_session_profile(request, data):
    request.session['profile'] = {
        'username': data['user']['username'],
        'first_name': data['user']['first_name'],
        'last_name': data['user']['last_name'],
        'email': data['user']['email'],
        'img': data['img'],
        'subscription': data['subscription'],
        'data_joined': get_date_joined_info(data['user']['date_joined'])
    }


def update_subscription_session_profile(request, subscription):
    request.session['profile']['subscription'] = subscription


def get_amount_payment(subscription):
    if subscription == "DEFAULT":
        return 0
    if subscription == "MAXIMUM":
        return 100
    if subscription == "ULTRA":
        return 200


def make_payment(request, subscription):
    user_info = {
        'username': request.session['profile']['username'],
        'subscription': subscription,
        'number': request.POST['card_number'],
        'exp_month': request.POST['exp_month'],
        'exp_year': request.POST['exp_year'],
        'cvc': request.POST['cvc']
    }
    response = requests.patch(config("SERVER_URL") + '/api/make-payment/', data=user_info)
    return response


def get_date_joined_info(date_s):
    date_d = datetime.datetime.strptime(date_s, '%Y-%m-%dT%H:%M:%S.%fZ')
    return date_d.strftime('%d.%m.%Y')


def get_date_joined_info_wo_float(date_s):
    date_d = datetime.datetime.strptime(date_s, '%Y-%m-%dT%H:%M:%SZ')
    return date_d.strftime('%d.%m.%Y')


def update_session_profile(request, data):
    request.session['profile']['username'] = data['username']
    request.session['profile']['email'] = data['email']
    request.session['profile']['first_name'] = data['first_name']
    request.session['profile']['last_name'] = data['last_name']


def update_image_session_profile(request, img):
    request.session['profile']['img'] = img


def set_session_counters(request, data):
    request.session['profile'].update(
        {
            'counters': {
                'ratings': data['ratings'],
                'articles': data['articles'],
                'disasters': data['disasters']
            }
        }
    )


def update_session_workplace(request, data):
    request.session['profile']['position'] = data['position']
    request.session['profile']['company'] = data['company']


def get_countries(language):
    if language == 'uk':
        return 'ua'
    if language == 'ru':
        return 'ru'
    if language == 'de':
        return 'de'
    if language == 'be':
        return 'be'
    if language == 'en':
        return  'gb'


def get_page_range(page, pages, size):
    if pages < size:
        return range(1, pages + 1)
    if page == 1:
        return range(1, size + 1)
    step = math.floor(size / 2)
    return range(page - step, page + step + 1)


def get_news_context(context, data, page, pages, total_, search):
    context.update({
        "news": [],
        "search": search
    })
    for i in data:
        context["news"].append({
            "title": i["title"],
            "description": "" if i["description"] is None else i["description"],
            "url": i["url"],
            "image": "" if i["urlToImage"] is None else i["urlToImage"],
            "publishedat": get_date_joined_info_wo_float(i["publishedAt"]),
            "source": i["source"]["name"],

        })
    context.update({
        "has_previous": False if int(page) == 1 else True,
        "previous_page_number": int(page) - 1,
        "number": int(page),
        "paginator": {
            "page_range": get_page_range(int(page), pages, 3),
            "num_pages": pages,
        },
        "has_next": False if int(page) == int(total_) else True,
        "next_page_number": int(page) + 1
    })
    return context


def change_data(data):
    for index, dataset in enumerate(data["datasets"]):
        list_ = list(data["datasets"][index]["data"])
        for i, item in enumerate(list_):
            list_[i] = round(item, 2)
        data["datasets"][index]["data"] = json.dumps(list_)
    return data


def get_data_from_file(data):
    all_info = pd.read_excel(data, engine='openpyxl')
    all_info = all_info.loc[:, ~all_info.columns.str.contains('^Unnamed')]
    all_info = all_info.dropna()
    labels = list(all_info["name"])
    clean_info = all_info.drop(columns=["name"])
    clean_info_t = clean_info.T
    dates = list(clean_info_t.index)
    result = {
        "dates": dates,
        "data": []
    }
    for column in clean_info_t:
        result["data"].append(
            {
                labels[column]: list(clean_info_t[column])
            }
        )
    return result

