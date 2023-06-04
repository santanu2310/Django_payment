from django.shortcuts import render, redirect
from django.contrib.auth import login,logout, authenticate
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect,HttpResponseBadRequest,HttpResponse
from django.contrib import messages
from .models import *
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

webhook_secret = 'whsec_13304eaf57e0917dc9be614247cbdff1d39036cf3d5045a41b80fdc0e64b2674'

# Create your views here.

class SignUpView(View):
    template = 'app/signup.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template)
    
    def post(self, request, *args, **kwargs):
        form = request.POST
        if form['password'] == form['confirmpassword']:
            try:
                new_user = User.objects.create_user(username=form['name'],password=form['password'])
                new_user.email = form['email']
                new_user.save()

                return redirect('home')
            except:
                messages.add_message(request, messages.INFO, "username already exist!")
        else:
            messages.add_message(request, messages.ERROR, "Password didn't match!")

        return render(request, self.template)

class SignInView(View):
    template = 'app/signin.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template)

    def post(self, request, *args, **kwargs):
        form = request.POST
        try:
            user = User.objects.get(username = form['name'])
            try:
                user = authenticate(username=form['name'],password=form['password'])
                login(request, user)
                return redirect('home')
            
            except:
                messages.add_message(request, messages.ERROR, "username or password is incorect")
        except:
            messages.add_message(request, messages.ERROR, "username doesn't exist!")
        return render(request, self.template)

@login_required(login_url='signin/')
def home(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request, 'app/index.html',context)


def create_checkout_session(request,id):
    product = Product.objects.get(id=id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    order = Order.objects.create(user = request.user, product = product, total_price = product.price)
    order.save()
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                    'currency': 'usd',
                    'product_data': {
                    'name': product.name,
                    'images':[product.get_image(),],
                    },
                    'unit_amount': int(product.price * 100),
                },
                'quantity': 1,
                }
            ],
            metadata={
                "product_id": order.id
            },
            mode='payment',
            client_reference_id=order.id,
            success_url=settings.CURRENT_DOMAIN + '/payment-successful',
            cancel_url=settings.CURRENT_DOMAIN + '/payment-cancelled',
        )
    except Exception as e:
        return HttpResponseBadRequest

    return redirect(checkout_session.url, code=303)

def payment_successful(request):    
    return render(request, 'app/success.html')


def payment_cancelled(request):
	return render(request, 'app/cancle.html')


@csrf_exempt
def webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        print('processing construct_event ...')
        event = stripe.Webhook.construct_event(
        payload, sig_header, webhook_secret
        )
        print('event successful ...')
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)


    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        
        session = event['data']['object']

        order = Order.objects.get(id=session["metadata"]["product_id"])
        order.stripe_payment_id = session['id']
        order.save()

        # Save an order in your database, marked as 'awaiting payment'
        order.payment_status = PAYMENT_STATUS[1][0]
        order.save()

        if session.payment_status == "paid":
            order.payment_status = PAYMENT_STATUS[2][0]
            order.save()

    elif event['type'] == 'checkout.session.payment_intent':
        session = event['data']['object']
        print('session >> payment_intent <<')

        # Fulfill the purchase
        

    elif event['type'] == 'checkout.session.async_payment_failed':
        session = event['data']['object']
        print('session >> async_payment_failed <<')

        # Send an email to the customer asking them to retry their order
        

    return HttpResponse(status=200)