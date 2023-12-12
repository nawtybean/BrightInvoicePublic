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
from django.shortcuts import render, HttpResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from invoice.models import Invoice
from system_management.models import (
    TenantUser
)
from system_management.utilities import (
    get_tenant
)
import pandas as pd
import numpy as np
from datetime import datetime


# Cache Control
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

User = get_user_model()


@login_required(login_url='/system_management/')
def dashboard(request):
    context = {}
    return render(request, "dashboard/dashboard.html", context)


decorators= (never_cache)
@method_decorator(decorators, name='dispatch')
class Dashboard(LoginRequiredMixin, View):
    """
    Dashboard class to handle the view for the dashboard page.

    Attributes:
        - LoginRequiredMixin: Ensures the user is logged in.
        - View: Django's base view class.
    """
    def get(self, request, *args, **kwargs):

        """
        Handle GET requests to display the dashboard.

        Args:
            - request: HTTP request object.
            - *args: Additional positional arguments.
            - **kwargs: Additional keyword arguments.

        Returns:
            - JSON response containing dashboard data or a 404 error message.
        """

        # Fetch tenant details and user ID
        tenant = get_tenant(request)
        user_id = request.user.id

        # Query for tenant user and filter based on user ID
        tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
        tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)

        if tenant_user_qs:
            try:
                # Generate dashboard data
                invoices = list(Invoice.objects.filter(tenant=tenant) \
                                            .values('invoice_data', 'number',
                                                        'due_date', 'po_number',
                                                        'discount', 'invoice_date',
                                                        'client__customer_name', 'status__name'))
                df = pd.json_normalize(invoices, 
                                        record_path=['invoice_data'], 
                                        meta=['number', 'due_date', 'po_number',
                                            'discount', 'invoice_date',
                                            'client__customer_name', 'status__name'])

                df['invoice_date'] = df['invoice_date'].dt.tz_localize(None)

                # Graph One
                graph_one = df.groupby(['client__customer_name'])['Line Total'].sum().reset_index(name ='Total Amount')
                graph_one_data = json.loads(graph_one.to_json(orient='records'))
                graph_one_keys = list(graph_one_data[0].keys())
                graph_one_x = list(graph_one_data[0].keys())[0]
                del graph_one_keys[0]

                # Graph Two
                graph_two = df.groupby(df.invoice_date.dt.month)['Line Total'].sum().reset_index(name ='Total Amount')
                graph_two_data = json.loads(graph_two.to_json(orient='records'))
                graph_two_keys = list(graph_two_data[0].keys())
                graph_two_x = list(graph_two_data[0].keys())[0]
                del graph_two_keys[0]

                # Graph Three
                graph_three = df.groupby(['Title'])['Quantity'].sum().reset_index(name ='Quantity')
                graph_three_data = json.loads(graph_three.to_json(orient='records'))
                graph_three_keys = list(graph_three_data[0].keys())
                graph_three_x = list(graph_three_data[0].keys())[0]
                del graph_three_keys[0]

                # Graph Four
                graph_four = df.groupby(['Title'])['Line Total'].sum().reset_index(name ='Line Total')
                graph_four_data = json.loads(graph_four.to_json(orient='records'))
                graph_four_keys = list(graph_four_data[0].keys())
                graph_four_x = list(graph_four_data[0].keys())[0]
                del graph_four_keys[0]

                # Cards Metrics
                sum_total_invoices = df['Line Total'].sum()
                count_over_due_invoices = df[df['status__name'] == 'Over Due']
                count_over_due_invoices = len(pd.unique(count_over_due_invoices['number']))
                sum_paid_invoices = df[df['status__name'] == 'Paid']['Line Total'].sum()
                invoice_this_month = graph_two[graph_two['invoice_date'] == graph_two['invoice_date'].max()]
                invoice_this_month = json.loads(invoice_this_month.to_json(orient='records'))
                current_this_month = datetime.today().strftime('%m')
                if int(invoice_this_month[0]['invoice_date']) == int(current_this_month):
                    invoice_this_month = invoice_this_month[0]['Total Amount']
                else:
                    invoice_this_month = 0


                graph_one_dict = {"data": graph_one_data,
                                "keys": graph_one_keys,
                                "x": graph_one_x}

                graph_two_dict = {"data": graph_two_data,
                                "keys": graph_two_keys,
                                "x": graph_two_x}

                graph_three_dict = {"data": graph_three_data,
                                    "keys": graph_three_keys,
                                    "x": graph_three_x}

                graph_four_dict = {"data": graph_four_data,
                                    "keys": graph_four_keys,
                                    "x": graph_four_x}

                cards = {"sum_total_invoices":sum_total_invoices,
                    "count_over_due_invoices": count_over_due_invoices,
                    "sum_paid_invoices": sum_paid_invoices,
                    "invoice_this_month": invoice_this_month}

                data = {
                        "graph_one_dict": graph_one_dict,
                        "graph_two_dict": graph_two_dict,
                        "graph_three_dict": graph_three_dict,
                        "graph_four_dict": graph_four_dict,
                        "cards": cards
                    }
            except:
                # If there is no data or an error occurs, default to 0 to avoid errors
                cards = {"sum_total_invoices":0,
                        "count_over_due_invoices": 0,
                        "sum_paid_invoices": 0,
                        "invoice_this_month": 0}
                
                # Create data dictionary with default values
                data = {
                        "graph_one_dict": 0,
                        "graph_two_dict": 0,
                        "graph_three_dict": 0,
                        "graph_four_dict": 0,
                        "cards": 0
                    }
                
            # Convert data to JSON format and return as an HTTP response
            data = json.dumps(data, indent=4, default=str)
            return HttpResponse(data, content_type='application/json')

        return HttpResponse(json.dumps({"data": '404'}, 
        indent=4, default=str), 
        content_type='application/json')