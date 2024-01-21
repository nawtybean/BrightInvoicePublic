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

import json
import re
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from system_management.utilities import (
    is_valid_date, get_tenant, http_https
)
from invoice.models import (
    Invoice,  Product
)
from system_management.models import (
    Tenant, TenantUser, Currency
)
from system_management.url_encryption import encrypt
from system_management.emails import send_invoice
from django.contrib.auth import get_user_model
from datetime import datetime
from django.db.models import Q

# Cache Control
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

User = get_user_model()
http_https = http_https()


@login_required(login_url='/system_management/')
def invoice_detail(request):
    """
    Render invoice details for a logged-in user.
    """

    # Fetching necessary data
    tenant = get_tenant(request)
    user_id = request.user.id
    tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
    tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)

    if tenant_user_qs:
        # Processing invoice details
        pk = request.session.get('pk')
        invoice = list(Invoice.objects.filter(Q(tenant=tenant) and Q(id=pk)) \
                                      .values('id', 'title', 'number',
                                              'due_date', 'po_number', 'discount',
                                              'notes', 
                                              'client__customer_name', 'client__address_line', 'client__phoneNumber', 
                                              'client__email_address', 'client__tax_number',
                                              'banking_details', 'invoice_date'))

        invoice_data = list(Invoice.objects.filter(Q(tenant=tenant) and Q(id=pk)) \
                                      .values('invoice_data'))[0]
        invoice_data = invoice_data['invoice_data']

        for i in range(len(invoice_data)):
            invoice_data[i]['line_total'] = round(float(invoice_data[i]['Quantity']) * float(invoice_data[i]['Price']), 2)

        encrypt_id = encrypt(list(Invoice.objects.filter(Q(tenant=tenant) and Q(id=pk)) \
                                      .values('number'))[0]['number'])

        product = list(Product.objects.filter(tenant=tenant) \
                                      .values('id', 'title', 'description',
                                              'quantity', 'price'))
        email_url = http_https + str(tenant) + ".brightinvoice.co.za/invoice/invoice-preview/" + encrypt_id

        request.session['invoice_number'] = invoice[0]['number']
        request.session['email_url'] = email_url

        # Creating context for rendering
        context = {     "product": product,
                        "invoice": invoice,
                        "encrypt_id": encrypt_id,
                        "invoice_data": invoice_data
                    }
        return render(request, "invoice/invoice-detail.html", context)
    return render(request, "invoice/invoice-detail.html")


@login_required(login_url='/system_management/')
def ajax_invoice_session(request):
    """
    Update the session with the selected invoice ID for AJAX requests.
    """
    id = request.POST.get('pk')
    request.session['pk'] = id
    request.session['from_app'] = True
    return JsonResponse({}, status=200)


decorators= (never_cache)
@method_decorator(decorators, name='dispatch')
class InvoiceDetail(LoginRequiredMixin, View):
    """
    Update invoice details based on user input.
    """

    login_url='/system_management/'


    def post(self, request, *args, **kwargs):
        """
        Handle POST request for updating invoice details.
        """
        tenant = get_tenant(request)
        user_id = request.user.id
        tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
        tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)

        if tenant_user_qs:
            if request.method == 'POST':
                data = json.load(request)
                invoice_data = data.get('invoice_data')
                po_number = data.get('po_number')
                discount_amount = data.get('discount_amount')
                if discount_amount == '':
                    discount_amount = 0
                invoice_date = data.get('invoice_date')
                if not is_valid_date(invoice_date):
                    invoice_date = datetime.today().strftime('%Y-%m-%d')
                due_date = data.get('due_date')
                if not is_valid_date(due_date):
                    due_date = datetime.today().strftime('%Y-%m-%d')
                notes = data.get('notes')
                invoice_number = request.session['invoice_number']

                clean_data = []
                for i in range(len(invoice_data)):
                    try:
                        invoice_data[i]['ProductID'] = re.sub('\s+', '', invoice_data[i]['ProductID'])
                        invoice_data[i]['ProductID'] = int(invoice_data[i]['ProductID'])
                        invoice_data[i]['Quantity'] = float(invoice_data[i]['Quantity'])
                        invoice_data[i]['Price'] = float(invoice_data[i]['Unit Price'])
                        invoice_data[i]['Line Total'] = float(invoice_data[i]['Unit Price']) * int(invoice_data[i]['Quantity'])

                        del invoice_data[i]['Select']
                        del invoice_data[i]['Unit Price']

                        clean_data.append(invoice_data[i].copy())
                    except:
                        continue

                entry = Invoice.objects.filter(tenant=tenant)
                entry = entry.get(number=invoice_number)
                entry.invoice_data = clean_data
                entry.po_number = po_number
                entry.discount = discount_amount
                entry.invoice_date = invoice_date
                entry.due_date = due_date
                entry.notes = notes
                entry.save()
        
            return HttpResponse(json.dumps({"data": '200'}, 
                                indent=4, default=str), 
                                content_type='application/json')
        return HttpResponse(json.dumps({"data": '404'}, 
                            indent=4, default=str), 
                            content_type='application/json')


decorators= (never_cache)
@method_decorator(decorators, name='dispatch')
class SendInvoice(LoginRequiredMixin, View):
    """
    Send the invoice to specified email addresses.
    """

    login_url='/system_management/'


    def post(self, request, *args, **kwargs):
        """
        Handle POST request for sending invoices via email.
        """
        
        tenant = get_tenant(request)
        user_id = request.user.id
        tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
        tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)

        # Get Currency Details
        tenant_vals = list(Tenant.objects.filter(Q(subdomain=tenant)).values())
        currency = tenant_vals[0]['currency_id']
        currency = list(Currency.objects.filter(pk=currency).values())
        currency = currency[0]['symbol']

        if tenant_user_qs:
            if request.method == 'POST':

                invoice_number = request.session['invoice_number']

                email_select = request.POST.get('emailSelect')
                invoice_amount = request.POST.get('invoice-amount')
                send_copy = request.POST.get('send_copy', False)
                if send_copy is not False:
                    send_copy = True
                email_message = request.POST.get('emailmessage')

                email_url = request.session['email_url']

                context = {
                    "email_select": email_select,
                    "send_copy": send_copy,
                    "email_message": email_message,
                    "email_url": email_url,
                    "invoice_amount": invoice_amount,
                    "currency": currency
                }
                send_invoice(request, context)

                entry = Invoice.objects.filter(tenant=tenant)
                entry = entry.get(number=invoice_number)
                entry.status_id = 4
                entry.save()

            return HttpResponse(json.dumps({"data": '200'}, 
                                indent=4, default=str), 
                                content_type='application/json')
        return HttpResponse(json.dumps({"data": '404'}, 
                            indent=4, default=str), 
                            content_type='application/json')