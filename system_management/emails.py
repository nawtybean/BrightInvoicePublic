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

from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.http import HttpResponseRedirect

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from system_management.utilities import generate_token

from system_management.utilities import (
     get_tenant
)

from system_management.models import (
    TenantUser
)


def send_confimration_email(request, user, subdomain):
    """
    Sends a confirmation email to the user upon registration or account confirmation.

    Args:
    - request: HttpRequest object.
    - user: User object representing the registered user.
    - subdomain: Subdomain string for creating the current site URL.

    Returns:
    - HttpResponseRedirect to the home page after sending the email.
    """
    # Constructing the current site URL using the subdomain
    current_site = subdomain + '.brightinvoice.co.za'

    # Loading the email template for the confirmation message
    template = loader.get_template('emails/confirm-email.txt')

    # Constructing the context for the email template
    context = {'user': user,
               'domain': current_site,
               'uid': urlsafe_base64_encode(force_bytes(user.pk)),
               'token': generate_token.make_token(user)}

    # Rendering the message using the template and context
    message = template.render(context)

    # Constructing the email with relevant details
    email = EmailMultiAlternatives(
        "BrightInvoice Email Verfication", message,
        "Congratulations " + "- Welcome to BrightInvoice" + "<hello@brightinvoice.co.za>" ,
        ["<" + user.email +">"]
    )

    # Specifying content type as HTML
    email.content_subtype = 'html'

    # Sending the email
    email.send()

     # Displaying a success message and redirecting to the home page
    messages.success(request, 'We sent a link to your email')
    return HttpResponseRedirect('/')


def send_invoice(request, context):
    """
    Sends an invoice email to the specified recipient with the invoice details.

    Args:
    - request: HttpRequest object.
    - context: Dictionary containing the necessary invoice details.

    Returns:
    - HttpResponseRedirect to the home page after sending the email.
    """

    # Getting the tenant's name from the request and formatting it
    tenant = str(get_tenant(request))
    tenant = tenant.title()

    # Extracting necessary details from the context
    email = context['email_select']
    send_copy = context["send_copy"]

    # Loading the email template for the invoice message
    template = loader.get_template('emails/invoice-email.txt')
    context = context

    # Constructing the message using the context and template
    message = template.render(context)

    # Constructing the email based on whether a copy needs to be sent
    if send_copy == True:
        email = EmailMultiAlternatives(
            tenant + " sent you an Invoice", message,
            "Invoice from " + tenant + "<" + request.user.email + ">",
            ["<" + email + ">", "<" + request.user.email + ">"]
        )
    else:
        email = EmailMultiAlternatives(
        tenant + " sent you an Invoice", message,
        "Invoice from" + tenant + "<" + request.user.email + ">",
        ["<" + email + ">"]
    )

    # Specifying content type as HTML
    email.content_subtype = 'html'

    # Sending the email
    email.send()

    # Displaying a success message and redirecting to the home page
    messages.success(request, 'We sent a link to your email')
    return HttpResponseRedirect('/')