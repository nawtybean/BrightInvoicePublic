# BrightInvoice

[![License](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/license/mit/)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/)
[![Django CI](https://github.com/nawtybean/BrightInvoicePublic/actions/workflows/django.yml/badge.svg)](https://github.com/nawtybean/BrightInvoicePublic/actions/workflows/django.yml)

<picture width="500">
  <source
    media="(prefers-color-scheme: dark)"
    src="https://brightinvoice.co.za/assets/img/logo/BrightInvoiceMin.png"
    alt="BrightInvoice Logo (dark)"
  />
  <img
    src="https://brightinvoice.co.za/assets/img/logo/BrightInvoiceWhiteMin.png"
    alt="BrightInvoice Logo (light)"
  />
</picture>

## Introduction

BrightInvoice is a simple Open-Source invoice generator solution for small businesses. Our user-friendly platform streamlines the invoicing process, saving you time and money.

BrightInvoice is designed for small businesses and freelancers, so it can be used in a wide range of industries, including but not limited to:

- Solar Installers
- Consulting
- Photography
- Graphic Design
- Video Editing
- Support Services
- Plumbers
- Electricians

Visit [BrightInvoice.co.za](https://brightinvoice.co.za/) for a live version of this app.


## Techstack

- Django 4.1.2
- Bootstrap 5
- HTML
- Javascript
- CSS

The live version is hosted on a VM by [Absolute Hosting](https://absolutehosting.co.za/) running Ubuntu 22.04, with all DNS records hosted on CloudFlare ensuring end to end SSL encryption.

Payment integration for recurring billing is handled through [PayFast](https://payfast.io/)


## Installation and Configuration

Let’s get started - Local development !
====================

Before we get started, it is important to note that this app is a Multi-Tenant app using ID's to seperate the tenants. The app uses subdomains i.e. yourcompany.brightinvoice.co.za to identify different tenants.

1\. Fork the Repo and Create Virtual Environment
=============================================

*   Fork the repo. 

cd to BrightInvoicePublic

*   Build virtual environment for the project

````python
python manage.py -m venv venv
````

this will create a virtual environment, now we need to activate it

On Windows

````
.\venv\bin\activate
````

On Linux

````
source venv/bin/Activate
````

Remember to create a new branch on your repo! Do not use master/main as this will cause issues later on for subsequent pull requests!


2\. Installing Requirements
=====================

After complete forking the repo, creating a venv and activating it, install the requirements.txt

````python
pip install -r requirements.txt
````

3\. Set hosts for local development
===================================
For local development, it is recommended to setup a psuedo domain (as this is a multi tenant app). Open your hosts file and add an entry that looks something like this: (There are a lot or resources online to add entries to your host file for your respective OS ). You can use any domain name you like.

````
127.0.0.1		acme.brightinvoice.co.za
````

4\. Database
================================

BrightInvoice uses PostgreSQL. Setup a PostgreSQL Server using a method you prefer. 

[Docker PostgreSQL](https://hub.docker.com/_/postgres)

[PostgreSQL for Windows](https://www.postgresql.org/download/windows/) - Remember to use PGAdmin to access the server

[PostgreSQL for Mac](https://www.postgresql.org/download/macosx/) - Remember to use PGAdmin to access the server

[PostgreSQL for Linux](https://www.postgresql.org/download/linux/) - Remember to use PGAdmin to access the server

Create a database with a name of your choosing once postgres is setup.


5\. Set the Environment Variables
================================

Create a .env file in the root directory of BrightInvoice, and set the following Variables

````python

# Dev/Prod
# Database
SECRET_KEY='<Your Django Secret Key Goes Here>'
DB_NAME='<Your Database Name Goes Here>'
DB_USER='<Your Database User Goes Here>'
DB_PASSWORD='<Your Database Password Goes sHere>'
DB_HOST='<Your Database Host Goes Here>'
DB_PORT='<Your Database Port Goes Here>'
# WEBSITE_HOSTNAME='*.<Your Domain Goes Here>' # Comment out for dev, enable for prod

# Payfast Details
SANDBOX_MODE=True/False
MERCHANT_ID='<Your Payfast Merchant ID Goes Here>'
MERCHANT_KEY='<Your Payfast Merchant Key Goes Here>'
PASS_PHRASE='<Your Payfast Pass Phrase Goes Here>'
CART_TOTAL=39 # The monthly recurring subscription price in Rands. Change as you want

# Email Settings
DEFAULT_EMAIL="<Your Email Goes Here>"
EMAIL_HOST_USER="<Your Email Goes Here>"
EMAIL_HOST_PASSWORD="<Your Password Goes Here>"
EMAIL_FROM_USER="<Your Email Goes Here>"
````



6\. Starting your BrightInvoice app
================================

The first step is to run migrations

````python
python manage.py migrate
````

Once migrations are successfull, there is a custom command under: 


````
└── root
    └── system_management
        └── managment
            └── commands
                └── make_super_user.py
````
You can double check and change the super user details in here.

Run this command using: 

````
python manage.py make_super_user
````

Once migrations are successfull and you have created the super user, you will find some sql insert statements in the following directoy:

````
└── root
    └── sql
        ├── insert_provinces.sql
        ├── currency_table_insert.sql
        ├── status_table_insert.sql
        └── terms_table_insert.sql
````

Run these scripts in order as shown above to insert data into their respective tables. 

Then we start the app using the domain you specified 

````
python manage.py runserver acme.brightinvoice.co.za:8000
````

7\. Let’s get started - Deployment  !
=================================

Follow this guide to deloy the app on your own server

[Deploy to your own server](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-22-04)


# Contributor Guide

Interested in contributing? Check out our
[CONTRIBUTING.md](https://github.com/nawtybean/BrightInvoicePublic/blob/main/CONTRIBUTING.md)
to find resources around contributing.

# Resources

- [Sponsorship](https://www.patreon.com/BrightInvoice) - We have a patreon account incase you want to sponsor this project
- [Creative Tim](https://www.creative-tim.com/]) - The theme provided in this project is provided by Creative Tim.
- [Django](https://www.djangoproject.com/) - The webframework for perfectionists with deadlines.
