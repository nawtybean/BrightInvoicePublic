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
from system_management.utilities import table_data
from system_management.models import TenantUser
from django.contrib.auth import get_user_model
from system_management.utilities import get_tenant
from invoice.models import Product

# Cache Control
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

User = get_user_model()


# This view requires authentication. Redirects to '/system_management/' if not logged in.
@login_required(login_url='/system_management/')
def products(request):
    # Renders the 'products.html' template with an empty context
    context = {}
    return render(request, "products/products.html", context)


# Decorator applied to the Products class to never cache its content
decorators= (never_cache)
@method_decorator(decorators, name='dispatch')
class Products(LoginRequiredMixin, View):
    """
    Handles product-related views including GET and POST requests.

    Methods:
    - get: Fetches product data for a specific tenant.
    - post: Handles creation and editing of product entries.
    """

    login_url='/system_management/'
    def get(self, request, *args, **kwargs):
        """
        Retrieves product data for a specific tenant.

        Parameters:
        - request: HTTP request object
        - args: Additional arguments
        - kwargs: Additional keyword arguments

        Returns:
        - JSON response containing product data
        """

        # Retrieves tenant information and user ID
        tenant = get_tenant(request)
        user_id = request.user.id
        tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
        tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)
        
        # Handles GET request to fetch product data for a particular tenant
        if request.method == 'GET':
            if tenant_user_qs:
                # Retrieves product data for the tenant
                product = Product.objects.filter(tenant=tenant).values()
                data = []
                for product in product:
                    product['Action'] = ""
                    data.append(product.copy())

                # Formats data into a table structure
                reorder_columns = ['id', 'title', 'description', 'quantity', 'price', 'Action']
                rename_columns = {'title': 'Product Name', 'description': 'Description', 
                                  'quantity': 'Quantity', 'price': 'Price', 'Action': 'Action'}
                data = table_data(data, reorder_columns, rename_columns)

                # Converts data to JSON format
                data = {
                    "data": data
                }
                data = json.dumps(data, indent=4, default=str)
                return HttpResponse(data, content_type='application/json')


    def post(self, request, *args, **kwargs):
        """
        Handles creation and editing of product entries.

        Parameters:
        - request: HTTP request object
        - args: Additional arguments
        - kwargs: Additional keyword arguments

        Returns:
        - JSON response indicating success or failure
        """

        # Handles POST requests to create or edit product entries
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

            entry = Product.objects.filter(tenant=tenant)
            entry = entry.get(id=pk)
            entry.delete()
            data = {
                    "data": 'data'
                }
            data = json.dumps(data, indent=4, default=str)
        
            return HttpResponse(data, content_type='application/json')
        
        if request.method == 'POST':
            product_name = request.POST.get('productname')
            product_description = request.POST.get('productdescription')
            price = request.POST.get('price')
            quantity = request.POST.get('quantity')
            product_id = int(request.POST.get('product-id'))
            
            if product_id <= 0:
                # Create the Entry
                entry = Product(
                    # Default tenant Filters
                    tenant=tenant,
                    tenant_user=user,

                    # add entry fields
                    title=product_name,
                    description=product_description,
                    quantity=quantity,
                    price=price,
                )
            else:
                # Edit the Entry
                entry = Product.objects.filter(tenant=tenant)
                entry = entry.get(id=product_id)
                # Default tenant filters
                entry.tenant = tenant
                entry.tenant_user = user

                # update entry fields
                entry.title=product_name
                entry.description=product_description
                entry.quantity=quantity
                entry.price=price
            entry.save()

            data = {
                    "data": 'data'
                }
            data = json.dumps(data, indent=4, default=str)
        
            return HttpResponse(data, content_type='application/json')


decorators= (never_cache)
@method_decorator(decorators, name='dispatch')
class EditProducts(LoginRequiredMixin, View):
    """
    Handles editing of product data.

    Methods:
    - get: Retrieves data for editing a specific product.
    """

    login_url='/system_management/'
    def get(self, request, *args, **kwargs):
        """
        Retrieves data for editing a specific product.

        Parameters:
        - request: HTTP request object
        - args: Additional arguments
        - kwargs: Additional keyword arguments

        Returns:
        - JSON response containing product data for editing
        """
        
        if request.method == 'GET':
            if 'pk' in request.GET:
                pk = request.GET['pk']
                product = Product.objects.get(id=pk)
                data = {
                    'id': product.id,
                    'product_name': product.title,
                    'product_description': product.description,
                    'price': product.price,
                    'quantity': product.quantity
                }
                data = json.dumps(data, indent=4, default=str)
    
                return HttpResponse(data, content_type='application/json')
            data = {
                "data": 'data'
            }
            data = json.dumps(data, indent=4, default=str)
    
            return HttpResponse(data, content_type='application/json')
        data = {
                "data": 'data'
            }
        data = json.dumps(data, indent=4, default=str)
    
        return HttpResponse(data, content_type='application/json')