import datetime
import json
import time

import pyrebase
import requests
import math

from decouple import config
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from client_side import settings
from client_side.apps.utils import utils
from client_side.settings import FIREBASE_CONFIG


def index(request):
    context = utils.set_init_variables(request)
    context.update(utils.set_amount_info())
    if "profile" in request.session:
        return render(request, "home.html", context)
    return render(request, "welcome.html", context)


def admin(request):
    current_language = get_language()
    return redirect(config("SERVER_URL") + "/" + current_language)


def sign_in(request):
    context = utils.set_init_variables(request)
    return render(request, "sign-in.html", context)


def sign_up(request):
    context = utils.set_init_variables(request)
    return render(request, "sign-up.html", context)


def sign_out(request):
    response = requests.post(config("SERVER_URL") + "/api/sign-out/")
    if response.status_code == 200:
        request.session.flush()
        return redirect("interface:index")
    messages.error(request, _("Sign_out_error"))
    return redirect("interface:home")


def forgot_password(request):
    context = utils.set_init_variables(request)
    return render(request, "forgot-password.html", context)


def sign_in_inner(request):
    if request.method == "POST":
        if "remember_me" in request.POST:
            request.session.set_expiry(0)
        user_info = {
            "username": request.POST["username"],
            "password": request.POST["password"],
        }
        response = requests.post(config("SERVER_URL") + "/api/sign-in/", data=user_info)
        if response.status_code == 200:
            utils.set_session_profile(request, json.loads(response.text))
            return redirect("interface:home")
        messages.warning(request, _("Sign_in_warning"))
        return redirect("interface:sign_in")
    messages.error(request, _("Sign_in_error"))
    return redirect("interface:sign_in")


def sign_up_inner(request):
    firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
    storage = firebase.storage()
    if request.method == "POST":
        user_info = {
            "username": request.POST["username"],
            "password": request.POST["password"],
            "first_name": request.POST["first_name"],
            "last_name": request.POST["last_name"],
            "email": request.POST["email"],
        }
        if "img" in request.FILES:
            filename = (
                    request.POST["username"]
                    + "__"
                    + str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))
                    + ".png"
            )
            file_save = default_storage.save(filename, request.FILES["img"])
            storage.child("files/" + filename).put("media/" + filename)
            delete = default_storage.delete(filename)
            user_info.update({"img": storage.child("files/" + filename).get_url(None)})
        response = requests.put(config("SERVER_URL") + "/api/sign-up/", data=user_info)
        if response.status_code == 201:
            utils.set_session_profile(request, json.loads(response.text))
            messages.success(request, _("Sign_up_successful"))
            return redirect("interface:buy_subscription")
        messages.warning(request, _("Sign_up_warning"))
        return redirect("interface:sign_up")
    messages.error(request, _("Sign_up_error"))
    return redirect("interface:sign_up")


def forgot_password_inner(request):
    if request.method == "POST":
        user_info = {
            "username": request.POST["username"],
            "password": request.POST["password"],
        }
        response = requests.patch(
            config("SERVER_URL") + "/api/reset-password/", data=user_info
        )
        if response.status_code == 200:
            utils.set_session_profile(request, json.loads(response.text))
            messages.success(request, _("Forgot_password_successful"))
            return redirect("interface:home")
        messages.warning(request, _("Make_payment_warning"))
        return redirect("interface:forgot_password")
    messages.error(request, _("Make_payment_error"))
    return redirect("interface:forgot_password")


def check_subscription(request):
    context = utils.set_init_variables(request)
    return render(request, "subscription-info.html", context)


def check_subscription_free(request):
    request.session["subscription"] = "DEFAULT"
    return redirect("interface:sign_up")


def check_subscription_maximum(request):
    request.session["subscription"] = "MAXIMUM"
    return redirect("interface:sign_up")


def check_subscription_ultra(request):
    request.session["subscription"] = "ULTRA"
    return redirect("interface:sign_up")


def buy_subscription(request):
    context = utils.set_init_variables(request)
    return render(request, "subscription-buy.html", context)


def buy_subscription_free(request):
    del request.session["subscription"]
    return redirect("interface:index")


def buy_subscription_maximum(request):
    request.session["subscription"] = "MAXIMUM"
    return redirect("interface:payment")


def buy_subscription_ultra(request):
    request.session["subscription"] = "ULTRA"
    return redirect("interface:payment")


def change_subscription(request):
    context = utils.set_init_variables(request)
    return render(request, "subscription-change.html", context)


def change_subscription_free(request):
    request.session["subscription"] = "DEFAULT"
    return redirect("interface:lower_subscription")


def change_subscription_maximum(request):
    request.session["subscription"] = "MAXIMUM"
    if utils.get_amount_payment(
            request.session["profile"]["subscription"]
    ) < utils.get_amount_payment("MAXIMUM"):
        return redirect("interface:payment")
    else:
        return redirect("interface:lower_subscription")


def change_subscription_ultra(request):
    request.session["subscription"] = "ULTRA"
    return redirect("interface:payment")


def create_payment(request):
    context = utils.set_init_variables(request)
    return render(request, "card.html", context)


def make_payment(request):
    if request.method == "POST":
        user_info = {
            "username": request.session["profile"]["username"],
            "subscription": request.session["subscription"],
            "number": request.POST["card_number"],
            "exp_month": request.POST["exp_month"],
            "exp_year": request.POST["exp_year"],
            "cvc": request.POST["cvc"],
        }
        response = requests.patch(
            config("SERVER_URL") + "/api/make-payment/", data=user_info
        )
        if response.status_code == 200:
            utils.update_subscription_session_profile(
                request, request.session["subscription"]
            )
            del request.session["subscription"]
            messages.success(request, _("Make_payment_successful"))
            return redirect("interface:home")
        messages.warning(request, _("Make_payment_warning"))
        return redirect("interface:payment")
    messages.error(request, _("Make_payment_error"))
    return redirect("interface:payment")


def lower_subscription(request):
    if request.method == "GET":
        user_info = {
            "username": request.session["profile"]["username"],
            "subscription": request.session["subscription"],
        }
        response = requests.patch(
            config("SERVER_URL") + "/api/lower-subscription/", data=user_info
        )
        if response.status_code == 200:
            utils.update_subscription_session_profile(
                request, request.session["subscription"]
            )
            del request.session["subscription"]
            messages.success(request, _("Lower_subscription_successful"))
            return redirect("interface:home")
        messages.warning(request, _("Lower_subscription_warning"))
        return redirect("interface:home")
    messages.error(request, _("Lower_subscription_error"))
    return redirect("interface:home")


def send_review(request):
    if request.method == "POST":
        review_data = {
            "username": request.session["profile"]["username"],
            "email": request.POST["email"],
            "review": request.POST["review"],
            "language": settings.LANGUAGE_CODE,
        }
        response = requests.put(
            config("SERVER_URL") + "/api/save-review/", data=review_data
        )
        if response.status_code == 200:
            messages.success(request, _("Review_successful"))
            return redirect("interface:home")
        messages.warning(request, _("Review_warning"))
        return redirect("interface:home")
    messages.error(request, _("Review_warning"))
    return redirect("interface:home")


def profile(request):
    context = utils.set_init_variables(request)
    user_data = {
        "username": request.session['profile']['username']
    }
    response = requests.get(
        config("SERVER_URL") + "/api/counters/", params=user_data
    )
    if response.status_code == 200:
        utils.set_session_counters(request, json.loads(response.text))
        response = requests.get(
            config("SERVER_URL") + "/api/workplace/", params=user_data
        )
        if response.status_code == 200:
            utils.update_session_workplace(request, json.loads(response.text))
            return render(request, "profile.html", context)
        messages.warning(request, _("Workplace_info_warning"))
        return render(request, "profile.html", context)
    messages.warning(request, _("Count_info_warning"))
    return render(request, "profile.html", context)


def change_profile(request):
    if request.method == "POST":
        user_info = {
            "username": request.session["profile"]["username"],
            "username_new": request.POST["username"],
            "first_name": request.POST["first_name"],
            "last_name": request.POST["last_name"],
            "email": request.POST["email"],
        }
        response = requests.patch(
            config("SERVER_URL") + "/api/change-profile/", data=user_info
        )
        if response.status_code == 200:
            utils.update_session_profile(request, request.POST)
            messages.success(request, _("User_info_successful_change"))
            return redirect("interface:profile")
        messages.warning(request, _("User_info_warning_change"))
        return redirect("interface:profile")
    messages.error(request, _("User_info_error_change"))
    return redirect("interface:profile")


def change_password(request):
    if request.method == "POST":
        user_info = {
            "username": request.session["profile"]["username"],
            "password": request.POST["password"],
        }
        response = requests.patch(
            config("SERVER_URL") + "/api/reset-password/", data=user_info
        )
        if response.status_code == 200:
            messages.success(request, _("Password_successful_change"))
            return redirect("interface:profile")
        messages.warning(request, _("Password_warning_change"))
        return redirect("interface:profile")
    messages.error(request, _("Password_error_change"))
    return redirect("interface:profile")


def change_image(request):
    firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
    storage = firebase.storage()
    if request.method == "POST":
        if "img" in request.FILES:
            filename = (
                    request.session["profile"]["username"]
                    + "__"
                    + str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))
                    + ".png"
            )
            file_save = default_storage.save(filename, request.FILES["img"])
            storage.child("files/" + filename).put("media/" + filename)
            delete = default_storage.delete(filename)
            user_info = {
                "username": request.session["profile"]["username"],
                "img": storage.child("files/" + filename).get_url(None),
            }
            response = requests.patch(
                config("SERVER_URL") + "/api/change-image/", data=user_info
            )
            if response.status_code == 200:
                utils.update_image_session_profile(
                    request, user_info['img']
                )
                messages.success(request, _("Image_successful_change"))
                return redirect("interface:profile")
            messages.warning(request, _("Image_warning_change_server"))
            return redirect("interface:profile")
        messages.warning(request, _("Image_warning_change_file"))
        return redirect("interface:profile")
    messages.error(request, _("Image_error_change"))
    return redirect("interface:profile")


def companies(request):
    context = utils.set_init_variables(request)
    if 'company' in request.session:
        del request.session['company']
    user_data = {
        "username": request.session['profile']['username'],
        "language": get_language()
    }
    response = requests.get(
        config("SERVER_URL") + "/api/companies/", params=user_data
    )
    if response.status_code == 200:
        all_response = json.loads(response.text)
        paginator = Paginator(all_response['companies'], 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context.update({
            'companies': page_obj,
            'markets': all_response['markets']
        })
        if request.is_ajax():
            return render(request, "pagination/companies.html", context)
        return render(request, "companies.html", context)
    messages.warning(request, _("Companies_info_warning"))
    return render(request, "companies.html", context)


def companies_action(request):
    if request.method == "POST":
        request.session['company'] = request.POST['company']
        if 'delete' in request.POST:
            return redirect("interface:companies_delete")
        if 'detail' in request.POST:
            return redirect("interface:companies_detail")
        messages.warning(request, _("Action_warning"))
        return redirect("interface:companies")
    messages.error(request, _("Action_error"))
    return redirect("interface:companies")


def companies_delete(request):
    user_data = {
        "id": request.session['company']
    }
    response = requests.delete(
        config("SERVER_URL") + "/api/companies/delete/", data=user_data
    )
    if response.status_code == 204:
        messages.success(request, _("Delete_company_successful"))
        return redirect('interface:companies')
    messages.warning(request, _("Delete_company_warning"))
    return redirect('interface:companies')


def companies_detail(request):
    context = utils.set_init_variables(request)
    user_data = {
        "language": get_language(),
        "id": request.session['company']
    }
    response = requests.get(
        config("SERVER_URL") + "/api/companies/detail/", params=user_data
    )
    if response.status_code == 200:
        company_info = json.loads(response.text)
        paginator = Paginator(company_info['users'], 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        company_info['users'] = page_obj
        context.update({
            'company': company_info,
            'users': company_info['all_users']
        })
        if request.is_ajax():
            return render(request, "pagination/companies-detail.html", context)
        return render(request, "companies-detail.html", context)
    messages.warning(request, _("Companies_info_warning"))
    return render(request, "companies-detail.html", context)


def companies_change(request):
    if request.method == "POST":
        user_info = {
            "name": request.POST["name"],
            "name_new": request.POST["name_new"],
            "website": request.POST["website"],
            "size": request.POST["size"],
            "revenue": request.POST["revenue"],
            "location": request.POST["location"],
            "description": request.POST["description"]
        }
        response = requests.patch(
            "http://127.0.0.1:8888" + "/api/companies/detail/edit/", data=user_info
        )
        if response.status_code == 200:
            messages.success(request, _("Company_info_successful_change"))
            return redirect("interface:companies_detail")
        messages.warning(request, _("Company_info_warning_change"))
        return redirect("interface:companies_detail")
    messages.error(request, _("Company_info_error_change"))
    return redirect("interface:companies_detail")


def companies_change_image(request):
    firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
    storage = firebase.storage()
    if request.method == "POST":
        if "img" in request.FILES:
            filename = (
                    request.POST["name"]
                    + "__"
                    + str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))
                    + ".png"
            )
            file_save = default_storage.save(filename, request.FILES["img"])
            storage.child("files/" + filename).put("media/" + filename)
            delete = default_storage.delete(filename)
            user_info = {
                "name": request.POST["name"],
                "img": storage.child("files/" + filename).get_url(None),
            }
            response = requests.patch(
                config("SERVER_URL") + "/api/companies/detail/image/", data=user_info
            )
            if response.status_code == 200:
                messages.success(request, _("Image_company_successful_change"))
                return redirect("interface:companies_detail")
            messages.warning(request, _("Image_company_warning_change_server"))
            return redirect("interface:companies_detail")
        messages.warning(request, _("Image_company_warning_change_file"))
        return redirect("interface:companies_detail")
    messages.error(request, _("Company_error_change"))
    return redirect("interface:companies_detail")


def companies_delete_users(request):
    if request.method == "POST":
        user_data = {
            "username": request.POST["username"],
            "name": request.POST["name"],
            "position": request.POST["position"]
        }
        response = requests.delete(
            config("SERVER_URL") + "/api/companies/detail/users/delete/", data=user_data
        )
        if response.status_code == 204:
            messages.success(request, _("Delete_users_company_successful"))
            return redirect('interface:companies_detail')
        messages.warning(request, _("Delete_users_company_warning"))
        return redirect('interface:companies_detail')
    messages.error(request, _("Delete_users_company_error"))
    return redirect('interface:companies_detail')


def companies_add_users(request):
    if request.method == "POST":
        user_data = {
            "username": request.POST["username"],
            "name": request.POST["name"],
            "position": request.POST["position"]
        }
        response = requests.put(
            config("SERVER_URL") + "/api/companies/detail/users/add/", data=user_data
        )
        if response.status_code == 200:
            messages.success(request, _("Add_users_company_successful"))
            return redirect('interface:companies_detail')
        messages.warning(request, _("Add_users_company_warning"))
        return redirect('interface:companies_detail')
    messages.error(request, _("Add_users_company_error"))
    return redirect('interface:companies_detail')


def companies_add(request):
    firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
    storage = firebase.storage()
    if request.method == "POST":
        if "img" in request.FILES:
            filename = (request.POST["name"]
                        + "__"
                        + str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))
                        + ".png"
                        )
            file_save = default_storage.save(filename, request.FILES["img"])
            storage.child("files/" + filename).put("media/" + filename)
            delete = default_storage.delete(filename)
            user_data = {
                "username": request.session["profile"]["username"],
                "email": request.session["profile"]["email"],
                "language": get_language(),
                "name": request.POST["name"],
                "website": request.POST["website"],
                "size": request.POST["size"],
                "revenue": request.POST["revenue"],
                "location": request.POST["location"],
                "description": request.POST["description"],
                "img": storage.child("files/" + filename).get_url(None),
                "market_id": request.POST["market_id"],
            }
            response = requests.put(
                config("SERVER_URL") + "/api/companies/add/", data=user_data
            )
            if response.status_code == 200:
                messages.success(request, _("Add_company_successful"))
                return redirect('interface:companies')
            messages.warning(request, _("Add_company_warning"))
            return redirect('interface:companies')
        messages.warning(request, _("Add_company_warning_files"))
        return redirect('interface:companies')
    messages.error(request, _("Add_company_error"))
    return redirect('interface:companies')


def reviews(request):
    context = utils.set_init_variables(request)
    response = requests.get(
        config("SERVER_URL") + "/api/reviews/"
    )
    if response.status_code == 200:
        paginator = Paginator(json.loads(response.text), 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context.update({
            'reviews': page_obj,
        })
        if request.is_ajax():
            return render(request, "pagination/reviews.html", context)
        return render(request, "reviews.html", context)
    messages.warning(request, _("Reviews_warning"))
    return render(request, "reviews.html", context)


def reviews_personal(request):
    context = utils.set_init_variables(request)
    user_info = {
        "username": request.session['profile']['username']
    }
    response = requests.get(
        config("SERVER_URL") + "/api/reviews/personal/", params=user_info
    )
    if response.status_code == 200:
        paginator = Paginator(json.loads(response.text), 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context.update({
            'reviews': page_obj,
            'review_user': True
        })
        if request.is_ajax():
            return render(request, "pagination/reviews.html", context)
        return render(request, "reviews.html", context)
    messages.warning(request, _("Reviews_personal_warning"))
    return render(request, "reviews.html", context)


def aid(request):
    context = utils.set_init_variables(request)
    return render(request, "aid.html", context)


def advices(request):
    context = utils.set_init_variables(request)
    user_info = {
        "username": request.session["profile"]["username"],
        "language": get_language()
    }
    response = requests.get(
        config("SERVER_URL") + "/api/advices/", params=user_info
    )
    if response.status_code == 200:
        all_response = json.loads(response.text)
        paginator = Paginator(all_response['advices'], 4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context.update({
            'advices': page_obj,
            'disasters': all_response['disasters'],
            'max_amount': all_response['max_amount']
        })
        if request.is_ajax():
            return render(request, "pagination/advices.html", context)
        return render(request, "advices.html", context)
    messages.warning(request, _("Advices_warning"))
    return render(request, "advices.html", context)


def advices_filter(request):
    context = utils.set_init_variables(request)
    type_ = request.POST["type"] if request.method == "POST" else request.GET["type"]
    rating = request.POST["rating"] if request.method == "POST" else request.GET["rating"]
    amount = request.POST["amount"] if request.method == "POST" else request.GET["amount"]
    user_info = {
        "id": type_,
        "rating": rating.replace(',', '.'),
        "amount": amount,
        "username": request.session["profile"]["username"],
        "language": get_language()
    }
    response = requests.get(
        config("SERVER_URL") + "/api/advices/filter/", params=user_info
    )
    if response.status_code == 200:
        all_response = json.loads(response.text)
        paginator = Paginator(all_response['advices'], 4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context.update({
            'advices': page_obj,
            'disasters': all_response['disasters'],
            'max_amount': all_response['max_amount'],
            'filter': True
        })
        if request.is_ajax():
            return render(request, "pagination/advices.html", context)
        return render(request, "advices.html", context)
    messages.warning(request, _("Advices_filter_warning"))
    return redirect('interface:advices')


def advices_rate(request):
    if request.method == "POST":
        user_info = {
            "id": request.POST["name"],
            "rating": request.POST["rating"],
            "username": request.session["profile"]["username"]
        }
        response = requests.put(
            config("SERVER_URL") + "/api/advices/rate/", data=user_info
        )
        if response.status_code == 201:
            messages.success(request, _("Advices_rate_successful"))
            return redirect('interface:advices')
        messages.warning(request, _("Advices_rate_warning"))
        return redirect('interface:advices')
    messages.error(request, _("Advices_rate_error"))
    return redirect('interface:advices')


def articles(request):
    context = utils.set_init_variables(request)
    user_info = {
        "username": request.session["profile"]["username"],
        "language": get_language()
    }
    response = requests.get(
        config("SERVER_URL") + "/api/articles/", params=user_info
    )
    if response.status_code == 200:
        all_response = json.loads(response.text)
        paginator = Paginator(all_response['articles'], 4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context.update({
            'articles': page_obj,
            'disasters': all_response['disasters'],
            'max_amount': all_response['max_amount']
        })
        if request.is_ajax():
            return render(request, "pagination/articles.html", context)
        return render(request, "articles.html", context)
    messages.warning(request, _("Articles_warning"))
    return render(request, "articles.html", context)


def articles_make(request):
    firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
    storage = firebase.storage()
    if request.method == "POST":
        if "img" in request.FILES:
            filename = (request.POST["name"]
                        + "__"
                        + str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))
                        + ".png"
                        )
            file_save = default_storage.save(filename, request.FILES["img"])
            storage.child("files/" + filename).put("media/" + filename)
            delete = default_storage.delete(filename)
            user_data = {
                "username": request.session["profile"]["username"],
                "name": request.POST["name"],
                "language": request.POST["language"],
                "type": request.POST["type"],
                "img": storage.child("files/" + filename).get_url(None),
                "text": request.POST["text"]
            }
            response = requests.put(
                config("SERVER_URL") + "/api/articles/create/", data=user_data
            )
            if response.status_code == 201:
                messages.success(request, _("Create_article_successful"))
                return redirect('interface:articles')
            messages.warning(request, _("Create_article_warning"))
            return redirect('interface:articles')
        messages.warning(request, _("Create_article_warning_files"))
        return redirect('interface:articles')
    messages.error(request, _("Create_article_error"))
    return redirect('interface:articles')


def articles_filter(request):
    context = utils.set_init_variables(request)
    type_ = request.POST["type"] if request.method == "POST" else request.GET["type"]
    rating = request.POST["rating"] if request.method == "POST" else request.GET["rating"]
    amount = request.POST["amount"] if request.method == "POST" else request.GET["amount"]

    user_info = {
        "id": type_,
        "rating": rating.replace(',', '.'),
        "amount": amount,
        "username": request.session["profile"]["username"],
        "language": get_language()
    }
    response = requests.get(
        config("SERVER_URL") + "/api/articles/filter/", params=user_info
    )
    if response.status_code == 200:
        all_response = json.loads(response.text)
        paginator = Paginator(all_response['articles'], 4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context.update({
            'articles': page_obj,
            'disasters': all_response['disasters'],
            'max_amount': all_response['max_amount'],
            'filter': True,
            'type': type_,
            'amount': amount,
            'rating': rating
        })
        if request.is_ajax():
            return render(request, "pagination/articles.html", context)
        return render(request, "articles.html", context)
    messages.warning(request, _("Articles_filter_warning"))
    return redirect('interface:articles')


def articles_rate(request):
    if request.method == "POST":
        user_info = {
            "id": request.POST["name"],
            "rating": request.POST["rating"],
            "username": request.session["profile"]["username"]
        }
        response = requests.put(
            config("SERVER_URL") + "/api/articles/rate/", data=user_info
        )
        if response.status_code == 201:
            messages.success(request, _("Articles_rate_successful"))
            return redirect('interface:articles')
        messages.warning(request, _("Articles_rate_warning"))
        return redirect('interface:articles')
    messages.error(request, _("Articles_rate_error"))
    return redirect('interface:articles')


def articles_delete(request):
    if request.method == "POST":
        user_data = {
            "id": request.POST["id"]
        }
        response = requests.delete(
            config("SERVER_URL") + "/api/articles/delete/", data=user_data
        )
        if response.status_code == 204:
            messages.success(request, _("Delete_articles_successful"))
            return redirect('interface:articles')
        messages.warning(request, _("Delete_articles_warning"))
        return redirect('interface:articles')
    messages.error(request, _("Delete_articles_error"))
    return redirect('interface:articles')


def articles_update(request):
    firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
    storage = firebase.storage()
    if request.method == "POST":
        if "img_article" in request.FILES:
            filename = (request.POST["name"]
                        + "__"
                        + str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S"))
                        + ".png"
                        )
            file_save = default_storage.save(filename, request.FILES["img_article"])
            storage.child("files/" + filename).put("media/" + filename)
            delete = default_storage.delete(filename)
            user_data = {
                "username": request.session["profile"]["username"],
                "name_old": request.POST["name_old"],
                "language": request.POST["language"],
                "name": request.POST["name"],
                "type": request.POST["type"],
                "img": storage.child("files/" + filename).get_url(None)
            }
            response = requests.patch(
                config("SERVER_URL") + "/api/articles/update/", data=user_data
            )
            if response.status_code == 200:
                messages.success(request, _("Update_article_successful"))
                return redirect('interface:articles')
            messages.warning(request, _("Update_article_warning"))
            return redirect('interface:articles')
        messages.warning(request, _("Update_article_warning_files"))
        return redirect('interface:articles')
    messages.error(request, _("Update_article_error"))
    return redirect('interface:articles')


def news(request):
    context = utils.set_init_variables(request)
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        sort = request.GET.get('sort', "popularity")
        user_info = {
            "language": get_language()
        }
        response = requests.get(config("SERVER_URL") + "/api/news/", params=user_info)
        if response.status_code != 200:
            messages.warning(request, _("Get_search_warning"))
            return render(request, 'news.html', context)
        all_response = response.json()
        search = all_response["news"]
        news_info = {
            "q": search,
            "sortBy": sort,
            "page": page,
            "apiKey": settings.NEWS_API,
            "language": get_language()
        }
        response = requests.get(config("NEWS_API_URL"), params=news_info)
        data = response.json()
        if response.status_code != 200:
            messages.warning(request, _("View_news_warning"))
            return render(request, 'news.html', context)
        total_ = data["totalResults"]
        pages = math.ceil(int(total_) / 20)
        data = data["articles"]
        context = utils.get_news_context(context, data, page, pages, total_, search)
        context["disasters"] = all_response["disasters"]
        context["sort"] = sort
        if request.is_ajax():
            return render(request, 'pagination/news.html', context)
        return render(request, 'news.html', context)
    messages.error(request, _("View_news_error"))
    return render(request, 'news.html', context)


def news_filter(request):
    context = utils.set_init_variables(request)
    user_info = {}
    if request.method == 'POST':
        page = request.POST.get('page', 1)
        sort = request.POST.get('sort', "popularity")
        user_info = {
            "language": request.POST["language"].replace(',', ' '),
            "id": request.POST["type"].replace(',', ' '),
            "language_base": get_language()
        }
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        sort = request.GET.get('sort', "popularity")
        user_info = {
            "language": request.GET["language"].replace(',', ' '),
            "id": request.GET["type"].replace(',', ' '),
            "language_base": get_language()
        }
    response = requests.get(config("SERVER_URL") + "/api/news/filter/", params=user_info)
    if response.status_code != 200:
        messages.warning(request, _("Filter_search_warning"))
        return render(request, 'news.html', context)
    all_response = response.json()
    search = all_response["news"]
    news_info = {
        "q": search,
        "sortBy": sort,
        "page": page,
        "apiKey": settings.NEWS_API,
    }
    response = requests.get(config("NEWS_API_URL"), params=news_info)
    data = response.json()
    if response.status_code != 200:
        messages.warning(request, _("View_news_warning"))
        return render(request, 'news.html', context)
    total_ = data["totalResults"]
    pages = math.ceil(int(total_) / 20)
    data = data["articles"]
    context = utils.get_news_context(context, data, page, pages, total_, search)
    context["disasters"] = all_response["disasters"]
    if request.method == 'POST':
        context["language"] = request.POST["language"]
        context["type"] = request.POST["type"]
    if request.method == 'GET':
        context["language"] = request.GET["language"]
        context["type"] = request.GET["type"]
    context["filter"] = True
    context["sort"] = sort
    if request.is_ajax():
        return render(request, 'pagination/news.html', context)
    return render(request, 'news.html', context)


def disasters(request):
    context = utils.set_init_variables(request)
    user_info = {
        "username": request.session["profile"]["username"],
        "language": get_language()
    }
    response = requests.get(
        config("SERVER_URL") + "/api/disasters/", params=user_info
    )
    if response.status_code == 200:
        all_response = json.loads(response.text)
        paginator = Paginator(all_response['disasters'], 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context.update({
            'disasters': page_obj,
            'types': all_response['types'],
            'companies': all_response['companies'],
            'max_term': all_response['max_term']
        })
        if request.is_ajax():
            return render(request, "pagination/disasters.html", context)
        return render(request, "disasters.html", context)
    messages.warning(request, _("Disasters_warning"))
    return render(request, "disasters.html", context)


def disasters_create(request):
    if request.method == "POST":
        user_data = {
            "username": request.session["profile"]["username"],
            "intensity": request.POST["intensity"],
            "term": request.POST["term"],
            "readiness": request.POST["readiness"],
            "type": request.POST["type"],
            "about": request.POST["about"]
        }
        response = requests.put(
            config("SERVER_URL") + "/api/disasters/create/", data=user_data
        )
        if response.status_code == 201:
            messages.success(request, _("Create_disasters_successful"))
            return redirect('interface:disasters')
        messages.warning(request, _("Create_disasters_warning"))
        return redirect('interface:disasters')
    messages.warning(request, _("Create_disasters_warning"))
    return redirect('interface:disasters')


def disasters_update(request):
    if request.method == "POST":
        user_data = {
            "id": request.POST["id_disaster"],
            "intensity": request.POST["intensity"],
            "term": request.POST["term"],
            "readiness": request.POST["readiness"],
            "type": request.POST["type"],
            "about": request.POST["about"]
        }
        response = requests.patch(
            config("SERVER_URL") + "/api/disasters/update/", data=user_data
        )
        if response.status_code == 200:
            messages.success(request, _("Update_disasters_successful"))
            return redirect('interface:disasters')
        messages.warning(request, _("Update_disasters_warning"))
        return redirect('interface:disasters')
    messages.warning(request, _("Update_disasters_warning"))
    return redirect('interface:disasters')


def disasters_delete(request):
    if request.method == "POST":
        user_data = {
            "id": request.POST["id_disaster"]
        }
        response = requests.delete(
            config("SERVER_URL") + "/api/disasters/delete/", data=user_data
        )
        if response.status_code == 204:
            messages.success(request, _("Delete_disasters_successful"))
            return redirect('interface:disasters')
        messages.warning(request, _("Delete_disasters_warning"))
        return redirect('interface:disasters')
    messages.error(request, _("Delete_articles_error"))
    return redirect('interface:disasters')


def disasters_filter(request):
    context = utils.set_init_variables(request)
    type_ = request.POST["type"] if request.method == "POST" else request.GET["type"]
    intensity = request.POST["intensity"] if request.method == "POST" else request.GET["intensity"]
    readiness = request.POST["readiness"] if request.method == "POST" else request.GET["readiness"]
    term = request.POST["term"] if request.method == "POST" else request.GET["term"]

    user_info = {
        "type": type_,
        "intensity": intensity,
        "readiness": readiness,
        "term": term,
        "username": request.session["profile"]["username"],
        "language": get_language()
    }
    response = requests.get(
        config("SERVER_URL") + "/api/disasters/filter/", params=user_info
    )
    if response.status_code == 200:
        all_response = json.loads(response.text)
        paginator = Paginator(all_response['disasters'], 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context.update({
            'disasters': page_obj,
            'types': all_response['types'],
            'max_term': all_response['max_term'],
            'companies': all_response['companies'],
            'filter': True,
            "type": type_,
            "intensity": intensity,
            "readiness": readiness,
            "term": term
        })
        if request.is_ajax():
            return render(request, "pagination/disasters.html", context)
        return render(request, "disasters.html", context)
    messages.warning(request, _("Disasters_filter_warning"))
    return redirect('interface:disasters')


def modelling(request):
    context = utils.set_init_variables(request)
    if request.method == "POST":
        request.session["disaster"] = {
            "id": request.POST["id_disaster"],
            "company": request.POST["company"]
        }
        return render(request, "modelling.html", context)
    messages.error(request, _("Modelling_error"))
    return redirect('interface:disasters')


def audience(request):
    context = utils.set_init_variables(request)
    user_info = {
        "company": request.session["disaster"]["company"],
        "language": get_language()
    }
    response = requests.get(
        config("SERVER_URL") + "/api/audience/", params=user_info
    )
    if response.status_code == 200:
        all_response = json.loads(response.text)
        paginator = Paginator(all_response['audiences'], 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context.update({
            'audiences': page_obj,
            'types': all_response['types'],
            'max_size': all_response['max_size']
        })
        if request.is_ajax():
            return render(request, "pagination/audience.html", context)
        return render(request, "audience.html", context)
    messages.warning(request, _("Audience_warning"))
    return render(request, "audience.html", context)


def audience_create(request):
    if request.method == "POST":
        user_data = {
            "company": request.session["disaster"]["company"],
            "size": request.POST["size"],
            "age_left": request.POST["age_left"],
            "age_right": request.POST["age_right"],
            "type": request.POST["type"],
            "features": request.POST["features"]
        }
        response = requests.put(
            config("SERVER_URL") + "/api/audience/create/", data=user_data
        )
        if response.status_code == 201:
            messages.success(request, _("Create_audience_successful"))
            return redirect('interface:audience')
        messages.warning(request, _("Create_audience_warning"))
        return redirect('interface:audience')
    messages.warning(request, _("Create_audience_warning"))
    return redirect('interface:audience')


def audience_update(request):
    if request.method == "POST":
        user_data = {
            "id": request.POST["id_audience"],
            "size": request.POST["size"],
            "age_left": request.POST["age_left"],
            "age_right": request.POST["age_right"],
            "type": request.POST["type"],
            "features": request.POST["features"]
        }
        response = requests.patch(
            config("SERVER_URL") + "/api/audience/update/", data=user_data
        )
        if response.status_code == 200:
            messages.success(request, _("Update_audience_successful"))
            return redirect('interface:audience')
        messages.warning(request, _("Update_audience_warning"))
        return redirect('interface:audience')
    messages.warning(request, _("Update_audience_warning"))
    return redirect('interface:audience')


def audience_delete(request):
    if request.method == "POST":
        user_data = {
            "id": request.POST["id_audience"]
        }
        response = requests.delete(
            config("SERVER_URL") + "/api/audience/delete/", data=user_data
        )
        if response.status_code == 204:
            messages.success(request, _("Delete_audience_successful"))
            return redirect('interface:audience')
        messages.warning(request, _("Delete_audience_warning"))
        return redirect('interface:audience')
    messages.error(request, _("Delete_audience_error"))
    return redirect('interface:audience')


def audience_filter(request):
    context = utils.set_init_variables(request)
    type_ = request.POST["type"] if request.method == "POST" else request.GET["type"]
    age_left = request.POST["age_left"] if request.method == "POST" else request.GET["age_left"]
    age_right = request.POST["age_right"] if request.method == "POST" else request.GET["age_right"]
    size = request.POST["size"] if request.method == "POST" else request.GET["size"]

    user_info = {
        "type": type_,
        "age_left": age_left,
        "age_right": age_right,
        "size": size,
        "company": request.session["disaster"]["company"],
        "language": get_language()
    }
    response = requests.get(
        config("SERVER_URL") + "/api/audience/filter/", params=user_info
    )
    if response.status_code == 200:
        all_response = json.loads(response.text)
        paginator = Paginator(all_response['audiences'], 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context.update({
            'audiences': page_obj,
            'types': all_response['types'],
            'max_size': all_response['max_term'],
            'filter': True,
            "type": type_,
            "age_left": age_left,
            "age_right": age_right,
            "size": size,
        })
        if request.is_ajax():
            return render(request, "pagination/audience.html", context)
        return render(request, "audience.html", context)
    messages.warning(request, _("Audience_filter_warning"))
    return redirect('interface:audience')


def audience_forecast(request):
    context = utils.set_init_variables(request)
    user_data = {
        "id": request.POST["id_audience"],
        "disaster": request.session["disaster"]["id"],
        "language": get_language()
    }
    response = requests.get(
        config("SERVER_URL") + "/api/audience/forecast/", params=user_data
    )
    if response.status_code != 200:
        messages.error(request, _("Audience_forecast_error"))
        return redirect('interface:audience')
    response_text = json.loads(response.text)
    context.update({
        'audience': response_text['audience'],
        'indicators': response_text['indicators']
    })
    return render(request, 'forecast-audience.html', context)


def company_forecast(request):
    context = utils.set_init_variables(request)
    if request.method != "POST":
        messages.warning(request, _("Company_forecast_warning"))
        return redirect('interface:modelling')
    user_data = {
        "id": request.session["disaster"]["company"],
        "disaster": request.session["disaster"]["id"],
        "language": get_language(),
        "info": request.POST["info"],
        "values": json.dumps(utils.get_data_from_file(request.FILES["data"]), indent=4)
    }
    response = requests.post(
        config("SERVER_URL") + "/api/company-forecast/", data=user_data
    )
    if response.status_code != 200:
        messages.error(request, _("Company_forecast_error"))
        return redirect('interface:modelling')
    response_text = json.loads(response.text)
    context.update(
        {
            "key": response_text["key"],
            "company": response_text["company"],
            "stop": False
        }
    )
    return render(request, 'forecast-company.html', context)


def company_forecast_done(request):
    new_data = {
        "key": request.GET["key"],
        "id": request.session["disaster"]["company"],
        "disaster": request.session["disaster"]["id"]
    }
    response = requests.post(
        config("SERVER_URL") + "/api/company-forecast/done/", data=new_data
    )
    if response.status_code != 200:
        context = {
            "key": request.GET["key"],
            "stop": False
        }
        return render(request, 'charts/forecast-company.html', context)
    response_text = json.loads(response.text)
    context = {
        "data": utils.change_data(response_text["data"]),
        "stop": True
    }
    return render(request, 'charts/forecast-company.html', context)


def company_stresstest(request):
    context = utils.set_init_variables(request)
    if request.method != "POST":
        messages.warning(request, _("Company_stresstest_warning"))
        return redirect('interface:modelling')
    user_data = {
        "id": request.session["disaster"]["company"],
        "disaster": request.session["disaster"]["id"],
        "language": get_language(),
        "info": request.POST["info"]
    }
    response = requests.post(
        config("SERVER_URL") + "/api/company-stresstest/", data=user_data
    )
    if response.status_code != 200:
        messages.error(request, _("Company_stresstest_error"))
        return redirect('interface:modelling')
    response_text = json.loads(response.text)
    context.update({
        'company': response_text['company'],
        'indicators': response_text['indicators']
    })
    return render(request, 'stresstest-company.html', context)


def market_forecast(request):
    context = utils.set_init_variables(request)
    if request.method != "POST":
        messages.warning(request, _("Market_forecast_warning"))
        return redirect('interface:modelling')
    user_data = {
        "id": request.session["disaster"]["company"],
        "disaster": request.session["disaster"]["id"],
        "language": get_language(),
        "method": request.POST["method"]
    }
    response = requests.get(
        config("SERVER_URL") + "/api/market-forecast/", params=user_data
    )
    if response.status_code != 200:
        messages.error(request, _("Market_forecast_error"))
        return redirect('interface:modelling')
    response_text = json.loads(response.text)
    context.update(
        {
            "market": response_text["market"],
            "key": response_text["key"],
            "stop": False
        }
    )
    return render(request, 'forecast-market.html', context)


def market_forecast_done(request):
    new_data = {
        "key": request.GET["key"],
        "id": request.session["disaster"]["company"],
        "disaster": request.session["disaster"]["id"]
    }
    response = requests.post(
        config("SERVER_URL") + "/api/market-forecast/done/", data=new_data
    )
    if response.status_code != 200:
        context = {
            "key": request.GET["key"],
            "stop": False
        }
        return render(request, 'charts/forecast-market.html', context)
    response_text = json.loads(response.text)
    response_text["data"]["datasets_first"] = response_text["data"]["datasets"][0]
    response_text["data"]["datasets_second"] = response_text["data"]["datasets"][1]
    context = {
        "data": response_text["data"],
        "stop": True
    }
    return render(request, 'charts/forecast-market.html', context)
