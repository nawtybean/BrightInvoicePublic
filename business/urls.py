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

from django.urls import path
from business.views.invoice import business, Invoices, EditInvoices
from business.views.invoice_preview import invoice_preview
from business.views.invoice_detail import invoice_detail, InvoiceDetail, SendInvoice, ajax_invoice_session

urlpatterns = [
    path('business', business, name='business'),
    path('invoice-detail', invoice_detail, name='invoice-detail'),
    path('invoice-preview/<str:pk>', invoice_preview, name='invoice-preview'),
    path('<int:pk>/edit-invoices/', EditInvoices.as_view(), name='edit-invoices'),

    # API
    path('invoices-crud/', Invoices.as_view(), name='invoices-crud'),
    path('invoice-detail-crud/', InvoiceDetail.as_view(), name='invoice-detail-crud'),
    path('send-invoice/', SendInvoice.as_view(), name='send-invoice'),

    # AJAX
    path('ajax-invoice-session', ajax_invoice_session, name='ajax-invoice-session')
    
]
