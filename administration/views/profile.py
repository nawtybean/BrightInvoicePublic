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
import os
from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from system_management.utilities import table_data
from django.contrib.auth import get_user_model, logout
from system_management.url_encryption import encrypt
from django.contrib.auth.hashers import make_password
from system_management.models import (
    TenantUser, Tenant, Currency
)
from system_management.utilities import (
    select_data, table_data, is_valid_date, 
    get_tenant, FailedJsonResponse, check_password,
    image_validation
)

# Cache Control
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

User = get_user_model()

# Function to handle user profile view
@login_required
def profile(request):
    # Get tenant information from the request
    tenant = get_tenant(request)
    user_id = request.user.id

    # Fetch user details using user ID
    user_details = list(User.objects.filter(pk=user_id) \
                                    .values('email', 'first_name',
                                            'last_name', 'phone', 'is_paid'))
    
    # Masking the password for security purposes
    for i in range(len(user_details)):
        user_details[i]['password'] = '**********'

    # Fetch tenant details based on the obtained tenant
    tenant_details = list(Tenant.objects.filter(subdomain=tenant) \
                                    .values('name', 'address',
                                            'telephone', 'free_invoice', 'bank_name',
                                            'bank_account_holder', 'bank_account_number'))
    
    # Fetch currency data from the database
    currency = list(Currency.objects.filter().values())
    currency = select_data(currency, 'name')

    # Prepare context with user, tenant, and currency details
    context = { "user_details": user_details,
                "tenant_details": tenant_details,
                "currency": currency}
    
    # Render the profile page with the context data
    return render(request, "administration/profile.html", context)


# Class-based view handling profile related actions
decorators = (never_cache)
@method_decorator(decorators, name='dispatch')
class Profile(LoginRequiredMixin, View):
    login_url='/system_management/'
    def get(self, request, *args, **kwargs):
        # Fetch tenant and user ID
        tenant = get_tenant(request)
        user_id = request.user.id

        # Fetch tenant user details
        tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
        tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)
        
        # Process the GET request for the profile
        if request.method == 'GET':
            if tenant_user_qs:

                # Fetch user and tenant details
                user_details = list(User.objects.filter(pk=user_id) \
                                    .values('id', 'email', 'first_name',
                                            'last_name', 'phone'))

                tenant_details = list(Tenant.objects.filter(subdomain=tenant) \
                                                    .values('id',  'name', 'address',
                                                            'telephone', 'image', 'currency__name', 
                                                            'bank_name', 'bank_account_holder', 'bank_account_number' ))
                
                # Mask password and encrypt user ID
                for i in range(len(user_details)):
                    user_details[i]['password'] = '**********'
                    user_details[i]['id'] = encrypt( user_details[i]['id'] )

                # Prepare data for table formatting
                data = []
                for user_details in user_details:
                    user_details['Action'] = ""
                    data.append(user_details.copy())

                reorder_columns = ['id', 'first_name', 'last_name', 
                                   'phone',  'email', 'password', 'Action']

                rename_columns = {'email': 'E-Mail', 'first_name': 'First Name', 
                                  'last_name': 'Last Name', 'phone': 'Phone Number', 
                                  'password': 'Password', 'Action': 'Action'}

                tenant_data = []
                for tenant_details in tenant_details:
                    try:
                        tenant_details['image_html'] = "<img src='/media/" + tenant_details['image'] + "' style='height:50px; width:50px'>"
                    except:
                        tenant_details['image_html'] = "<img src=''>"
                    tenant_details['Action'] = ""
                    tenant_data.append(tenant_details.copy())


                tenant_reorder_columns = ['id', 'image_html', 'name', 'address', 
                                         'telephone', 'currency__name', 'bank_name', 'Action']

                tenant_rename_columns = {'image_html': 'Company Logo', 'name': 'Company Name', 'address': 'Address', 
                                  'telephone': 'Company Phone', 'currency__name': 'Currency Name', 
                                  'bank_name': 'Bank Name', 'Action': 'Action'}

                # Format table data
                data = table_data(data, reorder_columns, rename_columns)
                tenant_data = table_data(tenant_data, tenant_reorder_columns, tenant_rename_columns)

                # Prepare response data
                data = {
                    "data": data,
                    "tenant_data": tenant_data
                }
                data = json.dumps(data, indent=4, default=str)

                # Return JSON response
                return HttpResponse(data, content_type='application/json')


    # Post request handler
    def post(self, request, *args, **kwargs):
        # Fetch tenant and user ID
        tenant = get_tenant(request)
        user_id = request.user.id

        # Fetch tenant user details
        tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
        tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)

        # Process the POST request for the profile
        if tenant_user_qs:
            if request.method == "POST":
                # Fetch data from the POST request
                data = request.POST
                first_name = data.get("firstname")
                last_name = data.get("lastname")
                phone_number = data.get("phonenumber")
                email = data.get("email")
                password = data.get("password")

                # Check if user exists with the provided email
                check_user = User.objects.filter(email=email)

                if check_user == False:
                    return FailedJsonResponse({"e": "E-mail Already Exists!"})

                # Update user information
                if password == "":
                    # user = request.user
                    entry = User.objects.get(id=user_id)
                    entry.first_name = first_name
                    entry.last_name = last_name
                    entry.phone = phone_number
                    entry.email = email
                    entry.save()

                else:
                    # Check password requirements
                    password_check = check_password(password)

                    if password_check == False:
                        return FailedJsonResponse({"e": "Password does not meet the required specifications!"})

                    # Encrypt the password and update user information
                    password = make_password(password, salt=None, hasher='default')

                    # user = request.user
                    entry = User.objects.get(id=user_id)
                    entry.first_name = first_name
                    entry.last_name = last_name
                    entry.phone = phone_number
                    entry.email = email
                    entry.password = password
                    entry.save()            

            # Return success response
            return HttpResponse(json.dumps({"data": '201'}, 
                    indent=4, default=str), 
                    content_type='application/json')

        # Return failure response
        return HttpResponse(json.dumps({"data": '404'}, 
                    indent=4, default=str), 
                    content_type='application/json')


decorators = (never_cache)
@method_decorator(decorators, name='dispatch')
class ProfileTenant(LoginRequiredMixin, View):
    """
    View for handling the profile of a tenant.
    """

    login_url='/system_management/'

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to update tenant profile.
        """
        # Retrieve the tenant associated with the request
        tenant = get_tenant(request)
        user_id = request.user.id

        # Fetch the TenantUser object related to the tenant and user_id
        tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
        tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)

        if tenant_user_qs:
            if request.method == "POST":
                
                # Retrieve necessary fields from the POST data
                data = request.POST
                company_name = data.get("companyname")
                company_address = data.get("address")
                company_phone = data.get("phone")
                currency_select = data.get("selectCurrency")
                bank = data.get("bank")
                accountholder = data.get("accountholder")
                accountnumber = data.get("accountnumber")
                # Handle the company logo file
                image_file = None
                file_path = ""
                if request.FILES:
                    if 'image_file' in request.FILES:
                        print('image_file')
                        image_file = request.FILES['image_file']

                        # Validate the uploaded image
                        image_check = image_validation(image_file)
                        if image_check == False:
                            return FailedJsonResponse({"e": "Not a Valid Image File!"})
                        
                        # Save the image and get its file path
                        file_path = Tenant(image=image_file)
                        file_path = file_path.image.url
                        file_extension = str(os.path.splitext(file_path)[1])

                        # Check if the file extension is allowed
                        if file_extension == '.jpg':
                            file_extension = True
                        elif file_extension == '.png':
                            file_extension = True
                        else:
                            file_extension = False

                        if file_extension == False:
                            return FailedJsonResponse({"e": "Not a Valid Image File extension. Only PNG or JPG Allowed!"})

                # Retrieve the tenant ID
                tenant_id = list(Tenant.objects.filter(subdomain=tenant).values())[0]['id']

                # Update the tenant's information with the provided data
                entry = Tenant.objects.get(id=tenant_id)
                entry.name = company_name
                entry.address = company_address
                entry.telephone = company_phone
                entry.currency_id = currency_select
                entry.bank_name = bank
                entry.bank_account_holder = accountholder
                entry.bank_account_number = accountnumber
                if image_file:
                    # Delete the old image and set the new one
                    entry.image.delete(save=False)
                    # add new image
                    entry.image = image_file
                    entry.image_path = file_path
                entry.save()

            # Return success response
            return HttpResponse(json.dumps({"data": '201'}, 
                    indent=4, default=str), 
                    content_type='application/json')
        
        # If conditions fail, return failure response
        return HttpResponse(json.dumps({"data": '404'}, 
            indent=4, default=str), 
            content_type='application/json')
