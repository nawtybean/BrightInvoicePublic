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
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager, LowercaseEmailField
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        (1, 'general'),
        (2, 'manager'),
        (3, 'director'),
        (4, 'admin'),
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    email = LowercaseEmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=500, blank=True, default=0)
    is_confirmed = models.BooleanField(default=False)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this site.'), )
    is_active = models.BooleanField(_('active'), default=True, help_text=_(
        'Designates whether this user should be treated as active. ''Unselect this instead of deleting accounts.'), )
    is_external = models.BooleanField(_('external'), default=True, help_text=_(
        'Designates whether this user should be treated as an external user.'), )
    is_paid = models.BooleanField(_('paid'), default=False, help_text=_(
        'Flag weather the user has paid or not.'), )

    created = models.DateTimeField(editable=False, default=datetime.now)
    # history = HistoricalRecords()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_type']
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    

class Currency(models.Model):
    name = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=100, null=True)
    symbol = models.CharField(max_length=100, null=True)

    created = models.DateTimeField(editable=False, default=datetime.now)
    modified = models.DateTimeField(default=datetime.now)

    user = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)

    # history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Currency'


class Tenant(models.Model):
    name = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    telephone = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    image_path = models.CharField(max_length=500, null=True)
    subdomain = models.CharField(max_length=255)
    free_invoice = models.IntegerField(blank=True, default=5)

    # bank fields
    bank_name = models.CharField(max_length=255, null=True)
    bank_account_holder = models.CharField(max_length=255, null=True)
    bank_account_number = models.CharField(max_length=255, null=True)


    # related fields
    currency =  models.ForeignKey(Currency, on_delete=models.RESTRICT, null=True)

    created = models.DateTimeField(editable=False, default=datetime.now)

    def __str__(self):
        return self.subdomain

    class Meta:
        verbose_name_plural = 'Tenant'


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'TenantAwareModel'


class TenantUser(TenantAwareModel):
    tenant_name = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created = models.DateTimeField(editable=False, default=datetime.now)

    def __str__(self):
        return self.tenant.name

    class Meta:
        verbose_name_plural = 'TenantUser'


class Provinces(models.Model):
    name = models.CharField(max_length=100, null=True)

    created = models.DateTimeField(editable=False, default=datetime.now)
    modified = models.DateTimeField(default=datetime.now)

    user = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)

    # history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Provinces'


class Terms(models.Model):
    name = models.CharField(max_length=100, null=True)

    created = models.DateTimeField(editable=False, default=datetime.now)
    modified = models.DateTimeField(default=datetime.now)

    user = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)

    # history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Terms'


class Status(models.Model):
    name = models.CharField(max_length=100, null=True)

    created = models.DateTimeField(editable=False, default=datetime.now)
    modified = models.DateTimeField(default=datetime.now)

    user = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)

    # history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Status'


