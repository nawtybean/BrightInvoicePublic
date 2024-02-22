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

from django.db import models
from system_management.models import (
        Status, Provinces, Currency, Terms,
        TenantAwareModel
)

from datetime import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone


class BankingDetails(TenantAwareModel):

    # basic Fields.
    details = models.CharField(null=True, blank=True, max_length=1000)
    
    # utility fields
    tenant_user = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)
    created = models.DateTimeField(editable=False, default=datetime.now)
    modified = models.DateTimeField(default=datetime.now)


    def __str__(self):
        return '{}'.format(self.details)

    class Meta:
        verbose_name_plural = 'BankingDetails'


class Customer(TenantAwareModel):

    # basic Fields.
    customer_name = models.CharField(null=True, blank=True, max_length=200)
    address_line = models.CharField(null=True, blank=True, max_length=200)
    # client_logo  = models.ImageField(default='default_logo.jpg', upload_to='company_logos', null=True)
    postal_code = models.CharField(null=True, blank=True, max_length=10)
    phoneNumber = models.CharField(null=True, blank=True, max_length=100)
    email_address = models.CharField(null=True, blank=True, max_length=100)
    tax_number = models.CharField(null=True, blank=True, max_length=100)

    # related fields
    province = models.ForeignKey(Provinces, on_delete=models.RESTRICT, null=True)

    # utility fields
    tenant_user = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)
    created = models.DateTimeField(editable=False, default=datetime.now)
    modified = models.DateTimeField(default=datetime.now)


    def __str__(self):
        return '{}'.format(self.customer_name)

    class Meta:
        verbose_name_plural = 'Customer'


class Product(TenantAwareModel):

    title = models.CharField(null=True, blank=True, max_length=100)
    description = models.TextField(null=True, blank=True)
    quantity = models.FloatField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)

    # related fields
    currency =  models.ForeignKey(Currency, on_delete=models.RESTRICT, null=True)

    #Utility fields
    tenant_user = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)
    created = models.DateTimeField(editable=False, default=datetime.now)
    modified = models.DateTimeField(default=datetime.now)


    def __str__(self):
        return '{}'.format(self.title)

    class Meta:
        verbose_name_plural = 'Product'


class Invoice(TenantAwareModel):

    title = models.CharField(null=True, blank=True, max_length=100)
    number = models.CharField(null=True, blank=True, max_length=100)
    due_date = models.DateField(null=True, blank=True)
    po_number = models.TextField(null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    invoice_data = models.JSONField(default=dict)
    invoice_date = models.DateTimeField(default=timezone.now, blank=True)
    has_viewed = models.BooleanField(default=False)
    view_dates = models.JSONField(default=dict)

    # related fields
    client = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.SET_NULL)
    terms = models.ForeignKey(Terms, on_delete=models.RESTRICT, null=True)
    status = models.ForeignKey(Status, on_delete=models.RESTRICT, null=True)
    banking_details = models.ForeignKey(BankingDetails, blank=True, null=True, on_delete=models.RESTRICT)

    # utility fields
    tenant_user = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)
    created  = models.DateTimeField(editable=False, default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return '{}'.format(self.number)
        

    class Meta:
        verbose_name_plural = 'Invoice'

    #This overrides the model save function so that we can  modify the self.modified field on save

    def save(self, *args, **kwargs):
        self.modified = timezone.now()
        super(Invoice,self).save(*args, **kwargs)
