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
from datetime import datetime
from django.contrib.auth import get_user_model


class PayFast(models.Model):

    # basic Fields.
    m_payment_id = models.CharField(null=True, blank=True, max_length=200)
    pf_payment_id = models.CharField(null=True, blank=True, max_length=200)
    payment_status = models.CharField(null=True, blank=True, max_length=10)
    item_name = models.CharField(null=True, blank=True, max_length=100)
    item_description = models.CharField(null=True, blank=True, max_length=100)
    amount_gross = models.CharField(null=True, blank=True, max_length=100)
    amount_fee = models.CharField(null=True, blank=True, max_length=100)
    amount_net = models.CharField(null=True, blank=True, max_length=100)
    billing_date = models.DateTimeField(default=datetime.now)
    cancel_date = models.DateTimeField(null=True, blank=True)
    token = models.CharField(null=True, blank=True, max_length=100)
    signature = models.CharField(null=True, blank=True, max_length=100)

    # related fields
    user = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)

    # utility fields
    created = models.DateTimeField(editable=False, default=datetime.now)
    modified = models.DateTimeField(default=datetime.now)


    def __str__(self):
        return '{}'.format(self.token)

    class Meta:
        verbose_name_plural = 'PayFast'