from django.shortcuts import render, redirect
from django.http import JsonResponse
import time
from amazon.models import User, Product
import json
from amazon.variables import get_localhost, get_computer_local_ip
from django.core.mail import send_mail
import random as rand
from django.conf import settings
# Create your views here.


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def login_session(request):
    try:
        request.session['logged']
        request.session['user_data']
    except Exception as e:
        request.session['user_data'] = None
        request.session['logged'] = False


def delete_sign_state_data(request):
    try:
        request.session['initial_state_data']
        request.session['initial_data']
    except Exception as e:
        request.session['initial_state_data'] = None
        request.session['initial_data'] = None
        return 0
    request.session['initial_state_data'] = None
    request.session['initial_data'] = None


def generate_otp():
    my_rand = rand.randint(10, 99)
    oter = str(int(time.time() * 1000))
    return f"{oter[len(oter)-4::]}{my_rand}"


def logout(request):
    login_session(request)
    if request.session['logged']:
        del request.session['user_data']
        return redirect('/')


def get_global_data(request):
    login_session(request)
    if request.session['logged']:
        print(request.session['user_data'])
        roda = User.objects.filter(
            gmail=request.session['user_data']['gmail'])[0]
        return JsonResponse({
            'gmail': roda.gmail,
            'username': roda.username,
            'cart': roda.cart,
            'orders': roda.orders,
            'detect': True
        })
    return JsonResponse({
        'gmail': '',
        'username': '',
        'cart': '',
        'orders': '',
        'detect': False
    })


def home(request):
    login_session(request)
    if request.session['logged']:
        return render(request, "home.html", {
            'gmail': request.session['user_data']['gmail'],
            'username': request.session['user_data']['username'],
            'cart': request.session['user_data']['cart'],
            'orders': request.session['user_data']['orders']
        })
    return render(request, "home.html")


def signup_auth(request):
    referer = request.META.get('HTTP_REFERER')
    print(referer)
    try:
        if 'https://amazonclonehakccer.herokuapp.com/signup' in referer:
            if is_ajax(request):
                print("Sd")
                if request.method == 'POST':
                    final_otp = request.POST.get('our_otp')
                    print(final_otp, request.session['otp'])
                    if final_otp == '':
                        return JsonResponse({
                            'taken': False,
                            'error': 'empty',

                        })
                    if final_otp != request.session['otp']:
                        return JsonResponse({
                            'taken': False,
                            'error': 'invalid',

                        })
                    data = request.session['initial_data']
                    my_user = User(username=data.get('username'),
                                   gmail=data.get('gamil'), password=data.get('password'))
                    my_user.save()
                    delete_sign_state_data(request)
                    return JsonResponse({
                        'taken': True,
                    })
            if request.method == 'GET':
                my_mail = request.GET.get('gmail')
                if my_mail != request.session['initial_state_data']:
                    print(my_mail, request.session['initial_state_data'])
                    request.build_absolute_uri('')
                    return redirect('/')
                return render(request, "signup_auth.html", {'gmail': request.session['initial_state_data']})
            return redirect('')
        return redirect('/')
    except Exception as e:
        return redirect('/')


def sign_up(request):
    if is_ajax(request):
        username = request.POST.get('username')
        gmail = request.POST.get('gamil')
        password = request.POST.get('password')
        arr = [False, False, False, False]
        print(request.POST)
        if username == '' or gmail == '' or password == '':
            return JsonResponse({"taken": False,
                                 })
        if len(str(username)) >= 3 and len(str(username)) <= 30:
            arr[0] = True
        if str(gmail):
            arr[1] = True
        if len(str(password)) > 8:
            arr[2] = True

        if len(User.objects.filter(gmail=gmail)) == 0:
            arr[3] = True
            request.session['initial_state_data'] = gmail
            request.session['initial_data'] = request.POST
            request.session['created'] = True
            request.session['otp'] = generate_otp()
            sending_mail(gmail, request.session['otp'])
            return JsonResponse({
                'taken': True,
                'validates': arr,
            })
        return JsonResponse({
            'taken': True,
            'validates': arr,

        })

    return render(request, "signup.html")


def single_prod(request):
    if request.method == 'GET':
        my_id = request.GET.get('id')
        if not str(my_id).isnumeric():
            return redirect('/')
        my_prod_data = Product.objects.filter(prod_id=int(my_id))
        if len(my_prod_data) <= 0:
            return redirect('/')

        same_prods_data = []
        all_prods = Product.objects.all()
        for i in all_prods:
            if i.category == my_prod_data[0].category:
                same_prods_data.append({
                    'prod_img': i.prod_img,
                    'title': i.title,
                    'desc': i.desc,
                    'stock': i.stock,
                    'cate': i.category,
                    'prod_price': i.price,
                    'prod_id': i.prod_id,
                })

        other_prods = []
        for i in all_prods:
            if i.category != my_prod_data[0].category:
                other_prods.append({
                    'prod_img': i.prod_img,
                    'title': i.title,
                    'desc': i.desc,
                    'stock': i.stock,
                    'cate': i.category,
                    'prod_price': i.price,
                    'prod_id': i.prod_id,
                })

        my_dat = {
            'prod_img': my_prod_data[0].prod_img,
            'title': my_prod_data[0].title,
            'desc': my_prod_data[0].desc,
            'stock': my_prod_data[0].stock,
            'cate': my_prod_data[0].category,
            'prod_price': my_prod_data[0].price,
            'prod_id': my_prod_data[0].prod_id,
            'same_prods': same_prods_data,
            'other_prods': other_prods
        }
        return render(request, "prod_full_desc.html", my_dat)
    return redirect('/')


def modify_cart(request):
    if is_ajax(request):
        print(request.session['logged'])
        if not request.session['logged']:
            return JsonResponse({
                'taken': False,
                'error': 'login',

            })
        my_id = request.GET.get('id')
        user_cart_data = json.loads(User.objects.filter(
            gmail=request.session['user_data']['gmail'])[0].cart)
        print(user_cart_data)
        if not str(my_id) in user_cart_data:
            user_cart_data.append(f"{my_id}")
            my_user = User.objects.filter(
                gmail=request.session['user_data']['gmail'])
            my_user.update(cart=json.dumps(user_cart_data))
            return JsonResponse({
                'tanishq': True,
                'taken': True,

            })
        return JsonResponse({
            'taken': False,

        })
    redirect('/')


def get_query_data(request):
    if is_ajax(request):
        if request.method == 'GET':
            my_ids = [i+1 for i in range(len(Product.objects.all()))]
            my_sears = []
            loca = request.GET.get('query')
            for l in range(len(my_ids)):
                my_single_dats = str(Product.objects.get(
                    prod_id=str(my_ids[l])).title)
                if loca.lower() == my_single_dats.lower()[0:len(loca)]:
                    my_sears.insert(0, my_single_dats)
                    print(my_sears)
                    continue
                if loca.lower() in my_single_dats.lower():
                    my_sears.append(my_single_dats)
            return JsonResponse({
                'lilo': my_sears
            })
    return JsonResponse({
        'lipa': 'Invalid Request Try again'
    })


def login(request):
    if is_ajax(request):
        if request.method == 'GET':
            gmail = request.GET.get('gmail')
            password = request.GET.get('password')
            print(request.GET)
            if gmail == '' or password == '':
                return JsonResponse({
                    'taken': False,
                    'error': 'empty',

                })
            if not len(password) >= 3 and len(password) <= 30:
                return JsonResponse({
                    'taken': False,
                    'error': 'invalid'
                })

            if len(User.objects.filter(gmail=gmail, password=password)) == 0:
                return JsonResponse({
                    'taken': False,
                    'error': 'not_found'
                })
            print("Hello World")
            single_user_data = User.objects.filter(
                gmail=gmail, password=password)[0]
            request.session['logged'] = True
            request.session['user_data'] = {
                'username': single_user_data.username,
                'gmail': single_user_data.gmail,
                'cart': single_user_data.cart,
                'orders': single_user_data.orders
            }
            return JsonResponse({
                'taken': True
            })
    if request.method == 'GET':
        if request.session['logged']:
            return redirect('/')
        return render(request, "login.html")


def prods(request):
    my_products = Product.objects.all()
    lis_of_products = []
    for i in range(len(my_products)):
        lis_of_products.append({
            'prodg': my_products[i].prod_img,
            'title': my_products[i].title,
            'desc': my_products[i].desc,
            'price': my_products[i].price,
            'cate': my_products[i].category,
            'stock': my_products[i].stock,
            'prod_id': my_products[i].prod_id
        })
    return render(request, "products.html", {'data': lis_of_products})


def cart_data(request):
    if is_ajax(request):
        if request.session['logged']:
            my_ser_gmail = request.session['user_data']['gmail']
            my_user_cart_data = User.objects.filter(gmail=my_ser_gmail)
            if len(my_user_cart_data) <= 0:
                return redirect('/')
            cart_data_id = list(json.loads(my_user_cart_data[0].cart))
            my_cart_data = []
            price = 0
            for j in range(len(cart_data_id)):
                my_prod_data = Product.objects.filter(
                    prod_id=int(cart_data_id[j]))[0]
                price += int(my_prod_data.price)
                my_cart_data.append({
                    'id': my_prod_data.prod_id,
                    'title': my_prod_data.title,
                    'desc': my_prod_data.desc,
                    'stock': my_prod_data.stock,
                    'prodg': my_prod_data.prod_img,
                    'price': my_prod_data.price
                })
            return JsonResponse({
                'data': my_cart_data,
                'total_price': price,
            })
        return redirect('login')
    return render(request, "my_cart.html")


def remove_item(request):
    if is_ajax(request):
        if request.session['logged']:
            item_id = str(request.GET.get('id'))
            my_ser_gmail = request.session['user_data']['gmail']
            my_user_cart_data = User.objects.filter(gmail=my_ser_gmail)
            if len(my_user_cart_data) <= 0:
                return redirect('/')
            cart_data_id = list(json.loads(my_user_cart_data[0].cart))
            if item_id == 'all':
                my_user_cart_data.update(cart=json.dumps([]))
                return JsonResponse({
                    'taken': True
                })
            if not item_id in cart_data_id:
                return JsonResponse({
                    'taken': False
                })
            cart_data_id.remove(item_id)
            my_user_cart_data.update(cart=json.dumps(cart_data_id))
            return JsonResponse({
                'taken': True
            })
        return redirect('login')


def search_prods(request):
    if request.method == 'GET':
        my_query_data = request.GET.get('query')
        my_whole_sers_data = Product.objects.all()
        list_of_prods = []
        if my_query_data == '':
            for k in range(len(my_whole_sers_data)):
                list_of_prods.append({
                    'prodg': my_whole_sers_data[k].prod_img,
                    'title': my_whole_sers_data[k].title,
                    'desc': my_whole_sers_data[k].desc,
                    'price': my_whole_sers_data[k].price,
                    'cate': my_whole_sers_data[k].category,
                    'stock': my_whole_sers_data[k].stock,
                    'prod_id': my_whole_sers_data[k].prod_id
                })
            return render(request, "filprods.html", {'data': list_of_prods})
        else:
            for j in range(len(my_whole_sers_data)):
                if my_query_data.lower() == my_whole_sers_data[j].title.lower()[0:len(my_query_data)]:
                    list_of_prods.append({
                        'prodg': my_whole_sers_data[j].prod_img,
                        'title': my_whole_sers_data[j].title,
                        'desc': my_whole_sers_data[j].desc,
                        'price': my_whole_sers_data[j].price,
                        'cate': my_whole_sers_data[j].category,
                        'stock': my_whole_sers_data[j].stock,
                        'prod_id': my_whole_sers_data[j].prod_id
                    })
                    continue
                if my_query_data.lower() in my_whole_sers_data[j].title.lower():
                    list_of_prods.append({
                        'prodg': my_whole_sers_data[j].prod_img,
                        'title': my_whole_sers_data[j].title,
                        'desc': my_whole_sers_data[j].desc,
                        'price': my_whole_sers_data[j].price,
                        'cate': my_whole_sers_data[j].category,
                        'stock': my_whole_sers_data[j].stock,
                        'prod_id': my_whole_sers_data[j].prod_id
                    })  # my_quer
            if len(list_of_prods) <= 0:
                return render(request, "filprods.html", {'my_quer': my_query_data})
            return render(request, "filprods.html", {'data': list_of_prods})


def profile(request):
    if request.method == 'GET':
        if request.session['logged']:
            my_gmail = request.session['user_data']['gmail']
            my_pass = User.objects.get(gmail=str(my_gmail)).password
            print(my_pass)
            return render(request, "profile.html", {'user': [my_gmail, str(request.session['user_data']['username']), str(my_pass)]})
        return redirect('/login')
    return redirect('/')


def sending_mail(gmail, token):
    subject = "Amazon Clone Wants Your Profile Needs to be verified"
    message = f"Paste This OTP in Authentication Field {token}"
    sender = settings.EMAIL_HOST_USER
    reciptent = [gmail]
    send_mail(subject, message, sender, reciptent)
