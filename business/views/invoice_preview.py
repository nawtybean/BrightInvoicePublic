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

from django.shortcuts import render
from business.models import (
    Invoice
)
from system_management.models import (
    Tenant, TenantUser, Currency
)
from system_management.utilities import (
    get_tenant
)
from system_management.url_encryption import decrypt
from django.db.models import Q
from PIL import Image
from datetime import datetime


def invoice_preview(request, pk):
    """
    View function to preview an invoice.

    Args:
    - request: HttpRequest object containing metadata about the request.
    - pk: Primary key of the invoice.

    Returns:
    - Renders the invoice preview template with context data or renders the 'invoice-not-found' template.
    """

    try: 
        # Check tenant and decrypt the primary key
        check_tenant = get_tenant(request)
        pk = decrypt(pk)

        # Retrieve tenant information
        tenant = pk.split('-')[1]
        tenant = Tenant.objects.filter(subdomain=tenant).first()

        # Verify if the tenant matches the request's tenant
        if check_tenant == tenant:

            try:
                # Check if the invoice is viewed from the app
                frm_app = request.session['from_app']
            except:
                frm_app = False

            # If this invoice is viewed from the email instead of the preview feature
            # Update invoice status if viewed from email
            if frm_app == False:
                invoice = Invoice.objects.get(Q(tenant=tenant) and Q(number=pk))

                # When an Invoice Is viewed from the email - this loads the date in json field in the db 

                # TODO : Add Behavior when the invoice is viewed multiple times

                current_view_date  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if isinstance(invoice.view_dates,dict):
                    invoice.view_dates = [current_view_date]
                elif isinstance(invoice.view_dates,list):
                    previous_dates = invoice.view_dates
                    invoice.view_dates = previous_dates.append(current_view_date)

                invoice.has_viewed = True
                invoice.save()

            # Retrieve invoice details
            invoice = list(Invoice.objects.filter(Q(tenant=tenant) and Q(number=pk)) \
                                            .values('number', 'invoice_date', 'due_date', 'po_number', 'discount', 
                                                    'client__customer_name', 'client__address_line',
                                                    'client__phoneNumber', 'client__email_address', 'client__tax_number',
                                                    'notes'))

            # Retrieve tenant and related user details
            tenant_vals = list(Tenant.objects.filter(Q(subdomain=tenant)).values())
            tenant_user_vals = list(TenantUser.objects.filter(Q(tenant=tenant)).values('tenant_name__email'))

            # Get image path
            image = '/media/' + tenant_vals[0]['image']

            # Retrieve currency and discount percentage
            discount_percent = invoice[0]['discount']
            currency = tenant_vals[0]['currency_id']
            currency = list(Currency.objects.filter(pk=currency).values())

            # Process invoice data
            invoice_data = list(Invoice.objects.filter(tenant=tenant, number=pk) \
                                               .values('invoice_data'))[0]
            invoice_data = invoice_data['invoice_data']

            sub_total, total = [], []
            for i in range(len(invoice_data)):
                invoice_data[i]['line_total'] = round(invoice_data[i]['Line Total'], 2)
                invoice_data[i]['sub_total'] = round(float(invoice_data[i]['Quantity']) * float(invoice_data[i]['Price']), 2)
                sub_total.append(invoice_data[i]['sub_total'])
                discount_sum = invoice_data[i]['sub_total'] / 100 * discount_percent
                total.append(round(float(invoice_data[i]['sub_total']) - float(discount_sum), 2))

            # Calculate totals
            s_total = round(sum(sub_total), 2)
            discount_percent
            discount_amount = round(sum(sub_total) - sum(total), 2)
            total = round(sum(total), 2)

            # Prepare context data
            context = { 'invoice_data': invoice_data,
                        'sub_total': s_total,
                        'discount_percent': discount_percent,
                        'discount_amount': discount_amount,
                        'total': total,
                        'invoice': invoice,
                        'tenant_vals': tenant_vals,
                        'tenant_user_vals': tenant_user_vals,
                        'image64': image,
                        'currency': currency
                        }
            
            # Render the invoice preview template with context data
            return render(request, "business/invoice-preview.html", context)
        else:
            # If tenant doesn't match, raise an exception
            raise Exception()
    except:
        # Render 'invoice-not-found' template for any exception
        return render(request, "business/invoice-not-found.html")