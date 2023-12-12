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

import os
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from dotenv import load_dotenv
load_dotenv('./.env')

email = os.environ['DEFAULT_EMAIL']


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Handles the logic for creating a new user with specific attributes.
        
        Args:
            *args: Variable positional arguments.
            **options: Variable keyword arguments.

        Comments:
            to use run 'python manage.py make_super_user'
        """
        password = make_password("root", salt=None, hasher='default')
        User = get_user_model()
        qs = User.objects.filter(email=email)
        
        # If the user does not exist, create a new user with the following attributes
        if not qs.exists():
            User.objects.create(first_name='Shaun',
                                last_name='De Ponte',
                                email=email,
                                phone='12345678',
                                password=password,
                                user_type=4,
                                is_confirmed=True,
                                is_staff=True,
                                is_active=True,
                                is_external=False,)