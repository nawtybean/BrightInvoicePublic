'''
@author: Shaun De Ponte, nawtybean3d@gmail.com

----- The MIT License (MIT) ----- 
Copyright (c) 2023, Shaun De Ponte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import requests
import urllib
import urllib.parse
import hashlib
import os
from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from system_management.models import TenantUser
from system_management.utilities import (
    select_data, table_data, get_a_uuid
)

from django.contrib.auth import get_user_model
from system_management.utilities import get_tenant
from payments.validate import (
    generateSignature, generateApiSignature
)
from datetime import datetime
from payments.validate import (
     pfValidIP, 
     pfValidPaymentData
)
from payments.models import PayFast
from django.conf import settings

User = get_user_model()
merchant_id = os.environ['MERCHANT_ID']
merchant_key = os.environ['MERCHANT_KEY']
pass_phrase = os.environ['PASS_PHRASE']
cart_total = os.environ['CART_TOTAL']

payfast_host = 'www.payfast.co.za'


# This function requires the user to be logged in. It initiates a payment process.
@login_required(login_url='/system_management/')
def payments(request):
    """
    Initiates a payment process.

    Retrieves user and tenant information, generates payment context,
    renders the payment page with necessary details.
    """

    # Retrieve tenant and user details
    tenant = get_tenant(request)
    user_id = request.user.id
    user_first_name = request.user.first_name
    user_last_name = request.user.last_name
    user_email = request.user.email

    # Filter tenant user queryset
    tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
    tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)

    if tenant_user_qs:
        # Payment URLs
        return_url = 'https://' + tenant.subdomain + '.brightinvoice.co.za/payments/payment-return'
        cancel_url = 'https://' + tenant.subdomain + '.brightinvoice.co.za/payments/payment-cancel'
        notify_url = 'https://' + tenant.subdomain + '.brightinvoice.co.za/payments/payment-notify'

        # Payment context with necessary details
        context = { 
                    # Merchant details
                    'merchant_id': merchant_id,
                    'merchant_key': merchant_key,
                    'return_url': return_url,
                    'cancel_url': cancel_url,
                    'notify_url': notify_url,
                    # Buyer details
                    'name_first': user_first_name,
                    'name_last': user_last_name,
                    'email_address': user_email,
                    # Transaction details
                    'm_payment_id': get_a_uuid(), #Unique payment ID to pass through to notify_url
                    'amount': str(cart_total),
                    'item_name': 'BrightInvoiceSubscription',
                    'item_description': 'BrightInvoiceSubscription',
                    'custom_int1': str(user_id),
                    'subscription_type': '1',
                    'recurring_amount': str(cart_total),
                    'frequency': '3',
                    'cycles': '0'

            }

        # Generate signature and update context
        signature = generateSignature(context, pass_phrase)
        context['signature'] = signature
        context['payfast_host'] = payfast_host

        return render(request, "payments/payments.html", context)


# Function to cancel a subscription
@login_required(login_url='/system_management/')
def cancel_subscription(request):
    """
    Cancels the user's subscription.

    Fetches necessary details to send a cancellation request to the PayFast API.
    Updates user and payment status accordingly.
    """

    # TODO: Filter the payfast table and fetch the latest token for the logged in user

    tenant = get_tenant(request)
    user_id = request.user.id
    tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
    tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)

    if tenant_user_qs:
        # Prepare data for PayFast cancellation request
        current_date = datetime.now()
        iso_date = current_date.strftime('%Y-%m-%dT%H:%M:%S')

        token = PayFast.objects.filter(user_id=user_id).latest('created')

        payload={}
        headers = { 
                    # Merchant details
                    'merchant-id': merchant_id,
                    'version': 'v1',
                    'timestamp': iso_date,
            }

        # Generate API signature for PayFast cancellation request
        signature = generateApiSignature(headers, pass_phrase)
        headers['signature'] = signature

        url = f'https://api.payfast.co.za/subscriptions/{token}/cancel'

        # Send request to PayFast API to cancel subscription
        response = requests.request("PUT", url, headers=headers, data=payload)

        # Update user and payment status on successful cancellation
        if response.status_code == 200:
            user = User.objects.get(pk=user_id)
            user.is_paid = False
            user.save()

            payfast = list(PayFast.objects.filter(token=token).values('id'))[0]['id']
            payfast = PayFast.objects.get(pk=payfast)
            payfast.payment_status = 'CANCELLED'
            payfast.cancel_date = datetime.today().strftime('%Y-%m-%d')
            payfast.save()

        return render(request, "payments/payments.html", headers)


# Function to handle payment notification
@require_POST
@csrf_exempt
def payment_notify(request):
    """
    Handles payment notifications from PayFast.

    Validates the payment data, updates user and payment status based on
    the received notification.
    """

    pfData = {}
    postData = request.body.decode('utf-8').split('&')
    for i in range(0,len(postData)):
        splitData = postData[i].split('=')
        pfData[splitData[0]] = splitData[1]

    check1 = pfValidIP(request)
    check2 = pfValidPaymentData(cart_total, pfData)

    if(check1 and check2):
        # Retrieve payment data
        m_payment_id = request.POST.get('m_payment_id')
        custom_int1 = request.POST.get('custom_int1')
        pf_payment_id  = request.POST.get('pf_payment_id')
        payment_status  = request.POST.get('payment_status')
        item_name   = request.POST.get('item_name')
        item_description = request.POST.get('item_description')
        amount_gross = request.POST.get('amount_gross')
        amount_fee = request.POST.get('amount_fee')
        amount_net = request.POST.get('amount_net')
        billing_date = request.POST.get('billing_date')
        token = request.POST.get('token')
        signature = request.POST.get('signature')
        user = User.objects.get(pk=int(custom_int1))

        # Save payment data into PayFast model
        entry = PayFast(m_payment_id=m_payment_id,
                        pf_payment_id=pf_payment_id,
                        payment_status=payment_status, 
                        item_name=item_name,
                        item_description=item_description,
                        amount_gross=amount_gross,
                        amount_fee=amount_fee,
                        amount_net=amount_net,
                        billing_date=billing_date,
                        token=token,
                        signature=signature,
                        user=user)
        entry.save()

        if payment_status == 'COMPLETE':
        # TODO: Change this to tenant paid is true... eventually...
            user.is_paid = True
        # TODO: Send an email confirmation
        else:
            user.is_paid = False
        user.save()
            # TODO: Send an email

        return HttpResponse(status=200)

    else:
        try:
            custom_int1 = request.POST.get('custom_int1')
            user = User.objects.get(pk=int(custom_int1))
            user.is_paid = False
            user.save()
        except:
            pass
        # TODO: Send an email saying something went wrong with the payment

        return HttpResponse(status=400)


# Function to handle payment return
@login_required(login_url='/system_management/')
def payment_return(request):
    """
    Handles the return from the payment process.

    Renders the return page after payment completion or cancellation.
    """

    context = { 
        }

    return render(request, "payments/return.html", context)


# Function to handle payment cancellation
@login_required(login_url='/system_management/')
def payment_cancel(request):
    """
    Handles payment cancellation.

    Renders the cancellation page for the payment process.
    """

    context = { 
        }

    return render(request, "payments/cancel.html", context)