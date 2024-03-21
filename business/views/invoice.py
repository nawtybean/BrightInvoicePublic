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
from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from system_management.utilities import (
    select_data, table_data, invoice_number_gen
)
from business.models import (
    Invoice, Customer
)
from system_management.models import (
    TenantUser, Terms, Status, Tenant
)
from django.contrib.auth import get_user_model
from system_management.utilities import get_tenant, FailedJsonResponse
from datetime import datetime

# Cache Control
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

User = get_user_model()


@login_required(login_url='/system_management/')
def business(request):
    context = {'title':'Business'}
    return render(request, "business/business.html", context)


decorators= (never_cache)
@method_decorator(decorators, name='dispatch')
class Invoices(LoginRequiredMixin, View):
    """
    View for handling invoice-related data.
    """
    login_url='/system_management/'
    def get(self, request, *args, **kwargs):
        """
        GET request handler.
        Fetches and organizes invoice data based on user status.
        """
        # Fetch tenant and user ID from the request
        tenant = get_tenant(request)
        user_id = request.user.id
        # Filter TenantUser based on tenant and user ID
        tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
        tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)

        # Check the request method
        if request.method == 'GET':
            if tenant_user_qs:

                user = User.objects.get(pk=int(user_id))

                 # Handling invoices based on user payment status
                if user.is_paid == False:
                    # Handling unpaid user invoice data
                    # Table Data
                    invoice = Invoice.objects.filter(tenant=tenant) \
                                            .values('id', 'title', 'number',
                                                    'due_date', 'client__customer_name',
                                                    'terms__name', 'status__name')
                    # Processing invoice data for display
                    data = []
                    for invoice in invoice:
                        invoice['Action'] = ""
                        data.append(invoice.copy())

                    reorder_columns = ['id', 'number', 'client__customer_name', 'title', 'due_date',
                                    'terms__name', 'status__name', 'Action']
                    rename_columns = { 'number': 'Invoice Number', 'client__customer_name': 'Client', 'title': 'Invoice Title',
                                    'due_date': 'Due Date', 
                                    'terms__name': 'Terms', 'status__name': 'Status', 'Action': 'Action'}

                elif user.is_paid == True:
                    # Handling paid user invoice data
                    # Table Data
                    invoice = Invoice.objects.filter(tenant=tenant) \
                                            .values('id', 'title', 'number',
                                                    'due_date', 'client__customer_name',
                                                    'terms__name', 'status__name', 'has_viewed')
                    # Processing invoice data for display
                    data = []
                    for invoice in invoice:
                        invoice['Action'] = ""
                        if invoice['has_viewed'] == True:
                            invoice['has_viewed'] = 'Yes'
                        else:
                            invoice['has_viewed'] = 'No'
                        data.append(invoice.copy())

                    reorder_columns = ['id', 'number', 'client__customer_name', 'title', 'due_date',
                                    'terms__name', 'status__name', 'has_viewed', 'Action']
                    rename_columns = { 'number': 'Invoice Number', 'client__customer_name': 'Client', 'title': 'Invoice Title',
                                    'due_date': 'Due Date', 
                                    'terms__name': 'Terms', 'status__name': 'Status', 'has_viewed': 'Has Client Viewed Invoice?','Action': 'Action'}

                # Generating table data for display
                data = table_data(data, reorder_columns, rename_columns)
                
                # Client Dropdown
                client = list(Customer.objects.filter(tenant=tenant).values())
                client = select_data(client, 'customer_name')

                # Terms Dropdown
                terms = list(Terms.objects.all().values())
                terms = select_data(terms, 'name')

                # Status Dropdown
                status = list(Status.objects.all().values())
                status = select_data(status, 'name')

                # Constructing JSON response
                data = {
                    "data": data,
                    "client": client,
                    "terms": terms,
                    "status": status
                }
                data = json.dumps(data, indent=4, default=str)
                return HttpResponse(data, content_type='application/json')


    def post(self, request, *args, **kwargs):
        """
        Handles POST requests for creating or editing invoice entries.

        Args:
        - request: HTTP request object
        - *args: Variable length argument list
        - **kwargs: Arbitrarily named arguments

        Returns:
        - HttpResponse: HTTP response object
        """

        # Get tenant information from the request
        tenant = get_tenant(request)
        user_id = request.user.id
        user = request.user

        # Filter tenant user queryset based on tenant and user ID
        tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
        tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)

        try:
            # Override request method if HTTP_X_METHODOVERRIDE is present (for DELETE requests)
            http_method = request.META['HTTP_X_METHODOVERRIDE']
            if http_method.lower() == 'delete':
                request.method = 'DELETE'
                request.META['REQUEST_METHOD'] = 'DELETE'
                request.DELETE = request.body
        except:
            pass

        if request.method == 'DELETE':
            # Delete the specified invoice entry
            pk = request.DELETE.decode('ascii').split('=')[1]

            entry = Invoice.objects.filter(tenant=tenant)
            entry = entry.get(id=pk)
            entry.delete()
            
            return HttpResponse(json.dumps({"data": '201'}, 
                        indent=4, default=str), 
                        content_type='application/json')
        
        if request.method == 'POST':
            # Handling POST requests for creating or editing invoice entries
            
            if request.user.is_paid:
                # Handling for paid users

                # Retrieve necessary data from the request
                client_name = request.POST.get('clientSelect')
                term_select = request.POST.get('termsSelect')
                status_select = request.POST.get('statusSelect')
                invoice_id = int(request.POST.get('invoice-id'))
                inv = invoice_number_gen(request)

                if invoice_id <= 0:
                    # Create a new invoice entry
                    entry = Invoice(
                        # Default tenant Filters
                        tenant=tenant,
                        tenant_user=user,

                        # add entry fields
                        number = inv,
                        client_id=client_name,
                        terms_id=term_select,
                        status_id=status_select,
                        due_date = datetime.today().strftime('%Y-%m-%d'),
                        invoice_date = datetime.today().strftime('%Y-%m-%d'),
                        discount=0,
                        invoice_data=[]
                    )

                else:
                    # Edit an existing invoice entry
                    entry = Invoice.objects.filter(tenant=tenant)
                    entry = entry.get(id=invoice_id)
                    # Default tenant filters
                    entry.tenant = tenant
                    entry.tenant_user = user

                    # update entry fields
                    # add entry fields
                    entry.client_id=client_name
                    entry.terms_id=term_select
                    entry.status_id=status_select
                entry.save()
                entry_id = entry.id
                request.session['pk'] = entry_id

                return HttpResponse(json.dumps({"data": '201'}, 
                        indent=4, default=str), 
                        content_type='application/json')

            else:
                # Handling for free tier users
                free_invoice = int(list(Tenant.objects.filter(subdomain=tenant) \
                                    .values('free_invoice'))[0]['free_invoice'])

                if  0 < free_invoice <= 5:
                    # User has remaining free invoices
                    # Retrieve necessary data from the request
                    client_name = request.POST.get('clientSelect')
                    term_select = request.POST.get('termsSelect')
                    status_select = request.POST.get('statusSelect')
                    invoice_id = int(request.POST.get('invoice-id'))
                    inv = invoice_number_gen(request)
                   
                    if invoice_id <= 0:
                        
                        # Create a new invoice entry
                        entry = Invoice(
                            # Default tenant Filters
                            tenant=tenant,
                            tenant_user=user,

                            # add entry fields
                            number = inv,
                            client_id=client_name,
                            terms_id=term_select,
                            status_id=status_select,
                            due_date = datetime.today().strftime('%Y-%m-%d'),
                            invoice_date = datetime.today().strftime('%Y-%m-%d'),
                            discount=0,
                            invoice_data=[]

                        )

                        # Update the free invoice count for the tenant
                        update_invoice = list(Tenant.objects.filter(subdomain=tenant) \
                                                            .values('id'))[0]['id']
                        update_invoice = Tenant.objects.get(id=update_invoice)
                        free_invoice = free_invoice - 1
                        update_invoice.free_invoice = free_invoice
                        update_invoice.save()

                    else:
                        # Edit an existing invoice entry
                        entry = Invoice.objects.filter(tenant=tenant)
                        entry = entry.get(id=invoice_id)
                        # Default tenant filters
                        entry.tenant = tenant
                        entry.tenant_user = user

                        # update entry fields
                        # add entry fields
                        entry.client_id=client_name
                        entry.terms_id=term_select
                        entry.status_id=status_select
                    entry.save()
                    entry_id = entry.id
                    request.session['pk'] = entry_id

                    return HttpResponse(json.dumps({"data": '201'}, 
                            indent=4, default=str), 
                            content_type='application/json')

                else:
                    return FailedJsonResponse({"e": "Free Tier Limit Reached. Subscribe to Continue"})

        # Return a response for other cases (if method is not DELETE or POST)
        return HttpResponse(json.dumps({"data": '400'}, 
                        indent=4, default=str), 
                        content_type='application/json')


decorators= (never_cache)
@method_decorator(decorators, name='dispatch')
class EditInvoices(LoginRequiredMixin, View):
    """
    View for editing invoices.

    Requires user authentication and prevents caching of responses.
    """
    login_url='/system_management/'
    def get(self, request, *args, **kwargs):
        """
        GET request handler for retrieving invoice data.

        Retrieves specific invoice data based on provided 'pk' (primary key) in the request.
        Returns JSON data representing the invoice if 'pk' is provided, otherwise returns a 400 error response.
        """

        if request.method == 'GET':
            if 'pk' in request.GET:
                pk = request.GET['pk']
                # Retrieve the invoice object using the provided primary key
                invoice = Invoice.objects.get(id=pk)
                data = {
                    'id': invoice.id,
                    'client_id': invoice.client_id,
                    'terms_id': invoice.terms_id,
                    'status_id': invoice.status_id,
                }
                # Serialize data to JSON format
                data = json.dumps(data, indent=4, default=str)
    
                # Return JSON response with invoice data
                return HttpResponse(data, content_type='application/json')

            return HttpResponse(json.dumps({"data": '400'}, 
                        indent=4, default=str), 
                        content_type='application/json')

        # Return a 400 error response if the request method is not GET
        return HttpResponse(json.dumps({"data": '400'}, 
                        indent=4, default=str), 
                        content_type='application/json')