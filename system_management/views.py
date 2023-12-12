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

from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings

# from django.template.loader import render_to_string

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, force_text, DjangoUnicodeDecodeError

from system_management.utilities import (
    FailedJsonResponse, get_tenant, generate_token, check_password, clean_domain
)
from system_management.models import Tenant, TenantUser

from .emails import send_confimration_email

User = get_user_model()


def change_password(request):
    """
    View function to handle password change.

    Args:
    - request: HttpRequest object

    Returns:
    - HttpResponse: Redirects to respective URLs based on form submission
    """

    if request.method == 'POST':
        # Creating a PasswordChangeForm object using request data
        form = PasswordChangeForm(request.user, request.POST)

        # Validating form data
        if form.is_valid():
            # Saving form data without committing to the database
            user = form.save(commit=False)
            user.is_confirmed = True
            user = form.save()

            # Updating session authentication hash after password change
            update_session_auth_hash(request, user)

            # Success message for password update
            messages.success(request, 'Your password was successfully updated!')

            # Checking for a session confirmation user
            confirm_user = request.session.get('confirm_user')

            # Handling specific confirmation user scenario
            if confirm_user == f"To_Confirm_{user.id}":
                del request.session['confirm_user']
                if user.is_external == True:
                    # Accessing user information and setting company ID in session
                    logged_in_user_id = user.id
                    logged_in_user_id = int(
                        list(User.objects.filter(pk=logged_in_user_id).values('company_id'))[0]['company_id']
                    )
                    request.session['company_pk'] = logged_in_user_id

                    # Success message for login and redirection
                    messages.success(request, "Login Successful")
                    url = '../administration/positions'
                    return redirect(url)
            # Redirection to dashboard after password change
            url = '../dashboard/dashboard'
            return redirect(url)
        else:
            # Error message for form data errors
            messages.error(request, 'Please correct the error below.')
    else:
        # Creating a PasswordChangeForm object for GET requests
        form = PasswordChangeForm(request.user)

    # Rendering the change password template with form data
    return render(request, 'registration/change_password.html', {
        'form': form
    })


def login_view(request):
    """
    Function to handle user login.

    Args:
    - request: HTTP request object containing user data.

    Returns:
    - Rendered login page or redirects to appropriate pages based on login status.
    """

    if request.method == "POST":
        # Retrieving username and password from the POST data
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticating user with provided credentials
        user = authenticate(request, username=username, password=password)
        if user is None:
            # If authentication fails, display error message and render login page
            messages.error(request, "Username and/or Password is incorrect!")
            return render(request, 'registration/login.html')

        if not user.is_confirmed:
            # If user's email is not confirmed, prompt for verification and logout
            messages.error(request, "You have not verfified your e-mail. Please check your inbox!")
            logout(request)
            return render(request, 'registration/login.html')

        if user.is_active:
            # If user is active, proceed to login and check for tenant association
            tenant = get_tenant(request)
            if tenant is not None:
                try:
                    user_id = user.id
                    # Filtering TenantUser objects for user and tenant association
                    tenant_user_qs = TenantUser.objects.filter(tenant=tenant)
                    tenant_user_qs = tenant_user_qs.filter(tenant_name=user_id)
                    if tenant_user_qs:
                        # If association exists, log in user and redirect to dashboard
                        tenant_user_id = tenant_user_qs.get(tenant=tenant)
                        login(request, user)
                        if request.user.is_authenticated:
                            if tenant_user_id.tenant_name.id == user_id:
                                messages.success(request, "Login Successful")
                                url = '../dashboard/dashboard'
                                return redirect(url)
                            else:
                                # Incorrect association, display error and logout
                                messages.error(request, "Username and/or Password is incorrect")
                                logout(request)
                                url = '/'
                                return redirect(url)
                    else:
                        # No association found, display error and logout
                        messages.error(request, "Username and/or Password is incorrect")
                        logout(request)
                        url = '/'
                        return redirect(url)

                except:
                    # Handling any unexpected errors
                    messages.error(request, "An error occurred")
                    logout(request)
                    url = '/'
                    return redirect(url)
            else:
                # No tenant found, display error and logout
                messages.error(request, "Username and/or Password is incorrect")
                logout(request)
                url = '/'
                return redirect(url)
        else:
            # If user is not active, display appropriate error message
            messages.error(request, "You are no longer active on the system!")

    # Context for rendering login page
    context = {}
    return render(request, 'registration/login.html', context)


def signup(request):
    """
    Handles user signup process.

    Args:
    - request: HttpRequest object containing metadata about the request made.

    Returns:
    - HttpResponse object: Renders a signup HTML page or returns a JSON response
                           indicating success or failure of the signup process.
    """

    if request.method == "POST":
        data = request.POST
        company_name = data.get("companyname")
        subdomain = data.get("subdomain")
        email = data.get("email")
        password = data.get("password")

        # Check the password
        password_check = check_password(password)
        # Clean domain
        subdomain = clean_domain(subdomain)
        # Check is user exists
        check_user = User.objects.filter(email=email)
        # Check if tenant exists
        check_tenant = Tenant.objects.filter(name=company_name)
        # Check if subdomain exists
        check_subdomain = Tenant.objects.filter(subdomain=subdomain)
        # Send errors if conditions are not met
        if check_user.exists():
            return FailedJsonResponse({"e": "E-mail Already Exists!"})
        elif check_tenant.exists():
            return FailedJsonResponse({"e": "Company Name Already Exists"})
        elif check_subdomain.exists():
            return FailedJsonResponse({"e": "Subdomain Already Exists"})
        elif password_check == False:
            return FailedJsonResponse({"e": "Password does not meet the required specifications!"})
        else:
            # Hash the password before saving it
            password = make_password(password, salt=None, hasher='default')

            # Create a new user
            new_user = User.objects.create(first_name='',
                                            last_name='',
                                            email=email,
                                            phone='',
                                            password=password,
                                            user_type=4,
                                            is_confirmed=False,
                                            is_staff=False,
                                            is_active=True,
                                            is_external=False,)
            new_user.save()
            new_user_id = new_user.id

            # Create a new tenant associated with the user
            new_tenant = Tenant(name=company_name,
                                address='',
                                telephone='',
                                email='',
                                subdomain=subdomain)
            new_tenant.save()
            new_tenant_id = new_tenant.id     

            # Link the user and tenant together
            tm = TenantUser(tenant_name_id=new_user_id, tenant_id=new_tenant_id)
            tm.save()

            try:
                send_confimration_email(request, new_user, subdomain)
            except:
                return FailedJsonResponse({"e": "Something went wrong, please try again later! Please contact us if problem persists."})

    context = {}
    return render(request, "registration/signup.html", context)


def activate_user(request, uidb64, token):
    """
    Activates a user account using the provided uidb64 and token.

    Args:
    - request: HttpRequest object representing the current request.
    - uidb64: A string representing the user's UID encoded in base 64.
    - token: A string representing the activation token.

    Returns:
    - If successful, redirects to the homepage after activating the user's account.
    - If unsuccessful, renders the 'registration/activate-fail.html' template with context.

    Raises:
    - None. Exceptions are caught and handled within the function.

    Comments:
    - Attempts to decode the UID and retrieve the corresponding user.
    - If decoding or user retrieval fails, sets 'user' to None.
    - Checks if the user exists and the token is valid using generate_token.check_token().
    - If the user exists and the token is valid, sets user.is_confirmed to True,
      saves the user, and displays a success message.
    - Redirects to the homepage upon successful activation.
    - If activation fails or user doesn't exist, renders an activation failure template.
    """

    try:
        # Attempt to decode the UID and retrieve the corresponding user
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except Exception as e:
        # If decoding or user retrieval fails, set 'user' to None
        user = None

    if user and generate_token.check_token(user, token):
        # If user exists and token is valid
        user.is_confirmed = True
        user.save()
        messages.success(request, "E-mail successfully verified. You can now log in")
        # Set the redirect URL to the homepage
        url = '/'
        return redirect(url)
    
    # Prepare context for activation failure template
    context = {'user': user}
    return render(request, 'registration/activate-fail.html', context)


