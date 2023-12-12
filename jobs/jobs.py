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

from payments.models import PayFast
from django.contrib.auth import get_user_model
from payments.models import PayFast
from datetime import datetime

User = get_user_model()

def schedule_billing():
    """
    Function to handle billing scheduling based on certain conditions.
    """
    # Fetch data from PayFast objects with payment_status as 'CANCELLED'
    data = list(PayFast.objects.filter(payment_status='CANCELLED') \
                                        .values('billing_date', 'cancel_date', 'user_id'))

    # Iterate through the fetched data
    for i in range(len(data)):
        # Extract necessary data for processing
        billing_day = int(data[i]['billing_date'].strftime('%d'))
        cancel_day = int(data[i]['cancel_date'].strftime('%d'))
        cancel_date = data[i]['cancel_date'].strftime('%Y-%m-%d')
        today = datetime.today().strftime('%Y-%m-%d')
        user_id = int(data[i]['user_id'])

        # Calculate remaining days based on billing and cancellation dates
        if billing_day <= cancel_day:
            days = billing_day - cancel_day
            days = abs(days)
            remaining_days = 30 - days
        elif billing_day >= cancel_day:
            remaining_days = billing_day - cancel_day

        # Calculate the difference in days between today and cancellation date
        d1 = datetime.strptime(today, "%Y-%m-%d")
        d2 = datetime.strptime(cancel_date, "%Y-%m-%d")
        delta = d1 - d2
        delta = delta.days

        # Check if the difference meets the conditions for setting user as unpaid
        if int(delta) >= remaining_days:
            user = User.objects.get(pk=user_id)
            user.is_paid = False
            user.save()
            
        print("remaining_days", remaining_days)
        print(f'Difference is {delta} days')
        print('-------------------------------')
