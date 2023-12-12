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
from django.db.models import Q
from system_management.utilities import table_data
from django.contrib.auth import get_user_model
from payments.models import PayFast
from datetime import datetime

User = get_user_model()


@login_required
def app_user(request):

   
    context = {}
    return render(request, "payments/return.html", context)


# class AppUser(View):
#     def get(self, request, *args, **kwargs):
#         data = {
#                 "data": 'app_user',
#                 "client_count": 2
#             }
#         data = json.dumps(data, indent=4, default=str)
#         return HttpResponse(data, content_type='application/json')


#     def post(self, request, *args, **kwargs):
#         pass


#     def put(self, request, *args, **kwargs):
#         pass


#     def delete(self, request, *args, **kwargs):
#         pass