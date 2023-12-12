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

import six
import os
import re
import string
from django.http import JsonResponse
from system_management.models import Tenant
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import uuid
from dateutil.parser import parse
from PIL import Image
from io import BytesIO
import base64
import pathlib

from django.contrib.auth import get_user_model

User = get_user_model()


class FailedJsonResponse(JsonResponse):
    def __init__(self, data):
        super().__init__(data)
        self.status_code = 400


class TokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_confirmed))

generate_token = TokenGenerator()


# get the host name
def get_hostname(request):
    """
    Extracts and returns the hostname from the request object.

    Args:
    - request: Request object

    Returns:
    - str: Hostname in lowercase
    """
    return request.get_host().split(':')[0].lower()


# check and get the signed in tenant
def get_tenant(request):
    """
    Retrieves the tenant based on the request's subdomain.

    Args:
    - request: Request object

    Returns:
    - Tenant object: Retrieved tenant object based on subdomain
    """
    hostname = get_hostname(request)
    subdomain = hostname.split('.')[0]
    return Tenant.objects.filter(subdomain=subdomain).first()


# get a UUID - URL safe, Base64
def get_a_uuid():
    """
    Generates and returns a URL-safe, Base64 UUID.

    Returns:
    - str: Generated UUID
    """
    return str(uuid.uuid4())


# generate invoice numbers
def invoice_number_gen(request):
    """
    Generates invoice numbers using tenant subdomain and UUID.

    Args:
    - request: Request object

    Returns:
    - str: Generated invoice number
    """
    tenant = get_tenant(request)
    inv_no = 'BRINV-' + tenant.subdomain + '-' + str(uuid.uuid4()).split('-')[4]
    return inv_no  


# use this table with data tables
def table_data(queryset, reorder_columns, rename_columns):
    """
    Generates a table compatible with data tables from the queryset.

    Args:
    - queryset: Queryset to convert to table data
    - reorder_columns: Columns to reorder
    - rename_columns: Dictionary to rename columns

    Returns:
    - list: Table data
    """
    df = []
    try:
        for query in queryset:
            record = {}
            for reorder_column in reorder_columns:
                value = query[reorder_column]
                if reorder_column in rename_columns:
                    record[rename_columns[reorder_column]] = value
                else:
                    record[reorder_column] = value
            if record:
                df.append(record)
    except:
        pass
    return df


def user_type_filter():
    """
    Provides a list of user types.

    Returns:
    - list: User type data
    """
    return [
        {
            "id": 1,
            "text": 'General'
        },
        {
            "id": 2,
            "text": 'Manager'
        },
        {
            "id": 3,
            "text": 'Director'
        },
        {
            "id": 4,
            "text": 'Administrator'
        }
    ]


# use this function to use select2 js
def select_data(queryset, column_name):
    """
    Prepares data for Select2 JS from the queryset.

    Args:
    - queryset: Queryset to convert to Select2 data
    - column_name: Name of the column to be used

    Returns:
    - list: Data formatted for Select2
    """
    df = []
    try:
        for query in queryset:
            record = {
                'id': query['id'],
                'text': query[column_name]
            }
            df.append(record)
        if df and len(df) > 1:
            df = sorted(df, key=lambda item: item['text'], reverse=False)
    except:
        pass
    return df


# check if the dates are valid
def is_valid_date(date):
    """
    Checks if a date string is a valid date.

    Args:
    - date: Date string to validate

    Returns:
    - bool: True if the date is valid, False otherwise
    """
    if date:
        try:
            parse(date)
            return True
        except:
            return False
    return False


# check if dev or prod and use http or https respectively
def http_https():
    """
    Determines whether to use HTTP or HTTPS based on environment.

    Returns:
    - str: HTTP/HTTPS string
    """
    if not 'WEBSITE_HOSTNAME' in os.environ:
        ssl = "http://"
    else:
        ssl = "https://"
    return ssl


# check if password meets minimum criteria
def check_password(p):
    """
    Checks if a password meets minimum criteria.

    Args:
    - p: Password string to check

    Returns:
    - bool: True if the password meets criteria, False otherwise
    """
    if (len(p) >= 8 and
        re.search(r'\d+', p) and
        re.search(r'[a-z]+', p) and
        re.search(r'[A-Z]+', p) and
        re.search(r'\W+', p) and not
        re.search(r'\s+', p)):
        return True
    else:
        return False


# clean the domain
def clean_domain(d):
    """
    Cleans a domain string by removing punctuation, spaces, and converting to lowercase.

    Args:
    - d: Domain string to clean

    Returns:
    - str: Cleaned domain string
    """
    new_string = d.translate(str.maketrans('', '', string.punctuation))
    new_string = new_string.replace(' ', '')
    new_string = new_string.lower()
    return new_string

 
def image_validation(image_file):
    """
    Validates an image file.

    Args:
    - image_file: Image file to validate

    Returns:
    - bool: True if the image is valid, False otherwise
    """
    try:
        v_image = Image.open(image_file)
        v_image = v_image.verify()
    except:
        v_image = False
    return v_image