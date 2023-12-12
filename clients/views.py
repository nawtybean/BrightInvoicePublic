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
from system_management.models import TenantUser
from django.db.models import Q
from system_management.utilities import (
    select_data, table_data
)
from django.contrib.auth import get_user_model
from system_management.utilities import get_tenant
from invoice.models import Customer, Provinces

# Cache Control
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

User = get_user_model()


@login_required(login_url='/system_management/')
def clients(request):
    """
    View function for rendering the clients page.

    Retrieves client data and renders the clients page template.
    """
    context = {}
    return render(request, "clients/clients.html", context)


decorators= (never_cache)
@method_decorator(decorators, name='dispatch')
class Clients(LoginRequiredMixin, View):
    """
    View class to manage client data.
    """
    login_url='/system_management/'
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests for client data.

        Retrieves client data and related information for display.
        """

        tenant = get_tenant(request)
        user_id = request.user.id
        tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
        tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)
        
        if request.method == 'GET':
            if tenant_user_qs:
                # Fetching customer data
                client = Customer.objects.filter(tenant=tenant) \
                                         .values('id', 'customer_name', 'address_line',
                                                 'postal_code', 'phoneNumber', 'email_address',
                                                 'tax_number')
                
                # Processing and formatting client data
                data = []
                for client in client:
                    client['Action'] = ""
                    data.append(client.copy())

                reorder_columns = ['id', 'customer_name', 'address_line', 'postal_code', 
                                   'phoneNumber', 'email_address', 'tax_number', 'Action']

                rename_columns = {'customer_name': 'Customer Name', 'address_line': 'Address', 
                                  'postal_code': 'Post Code', 'phoneNumber': 'Phone Number', 
                                  'email_address': 'E-Mail', 'tax_number':'Tax Number', 
                                  'Action': 'Action'}

                data = table_data(data, reorder_columns, rename_columns)

                # Select Dropdown Data
                provinces = list(Provinces.objects.all().values())
                provinces = select_data(provinces, 'name')

                data = {
                    "data": data,
                    "provinces": provinces
                }
                data = json.dumps(data, indent=4, default=str)
                return HttpResponse(data, content_type='application/json')


    def post(self, request, *args, **kwargs):
        """
        Handles POST requests for client data.

        Processes client data for creation or modification.
        """
        tenant = get_tenant(request)
        user_id = request.user.id
        user = request.user
        tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
        tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)

        try:
            http_method = request.META['HTTP_X_METHODOVERRIDE']
            if http_method.lower() == 'delete':
                request.method = 'DELETE'
                request.META['REQUEST_METHOD'] = 'DELETE'
                request.DELETE = request.body
        except:
            pass

        if request.method == 'DELETE':
            # Delete the Entry
            pk = request.DELETE.decode('ascii').split('=')[1]

            entry = Customer.objects.filter(tenant=tenant)
            entry = entry.get(id=pk)
            entry.delete()
            return HttpResponse(json.dumps({"data": '200'}, 
                    indent=4, default=str), 
                    content_type='application/json')
        
        if request.method == 'POST':
            client_name = request.POST.get('customername')
            address = request.POST.get('adress')
            postcode = "1234"
            phone_number = request.POST.get('phonenumber')
            email = request.POST.get('email')
            tax_number = request.POST.get('taxnumber')
            province = 1
            client_id = int(request.POST.get('client-id'))

            
            if client_id <= 0:
                # Create the Entry
                entry = Customer(
                    # Default tenant Filters
                    tenant=tenant,
                    tenant_user=user,

                    # add entry fields
                    customer_name=client_name,
                    address_line=address,
                    postal_code=postcode,
                    phoneNumber=phone_number,
                    email_address=email,
                    tax_number=tax_number,
                    province_id=province,
                )
            else:
                # Edit the Entry
                entry = Customer.objects.filter(tenant=tenant)
                entry = entry.get(id=client_id)
                # Default tenant filters
                entry.tenant = tenant
                entry.tenant_user = user

                # update entry fields
                entry.customer_name = client_name
                entry.address_line = address
                entry.postal_code = postcode
                entry.phoneNumber = phone_number
                entry.email_address = email
                entry.tax_number = tax_number
                entry.province_id = province
            entry.save()

            return HttpResponse(json.dumps({"data": '200'}, 
                    indent=4, default=str), 
                    content_type='application/json')

decorators= (never_cache)
@method_decorator(decorators, name='dispatch')
class EditClients(LoginRequiredMixin, View):
    """
    View class to edit client data.
    """
     
    login_url='/system_management/'
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to fetch client data for editing.

        Fetches client data based on ID for editing purposes.
        """

        if request.method == 'GET':
            if 'pk' in request.GET:
                pk = request.GET['pk']
                client = Customer.objects.get(id=pk)

                # Formatting client data for editing
                data = {
                    'id': client.id,
                    'customer_name': client.customer_name,
                    'address_line': client.address_line,
                    'postal_code': client.postal_code,
                    'phoneNumber': client.phoneNumber,
                    'email_address': client.email_address,
                    'tax_number': client.tax_number,
                    'province_id': client.province.id
                }
                
                data = json.dumps(data, indent=4, default=str)
    
                return HttpResponse(data, content_type='application/json')

            return HttpResponse(json.dumps({"data": '404'}, 
                    indent=4, default=str), 
                    content_type='application/json')

        return HttpResponse(json.dumps({"data": '404'}, 
                    indent=4, default=str), 
                    content_type='application/json')