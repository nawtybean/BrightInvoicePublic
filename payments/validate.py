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

import requests
import hashlib
import urllib.parse
from werkzeug.urls import url_parse
import socket


def pfValidIP(request):
    """
    Validates the incoming request's Referer IP against a predefined list of valid IP addresses.
    
    Args:
    - request: The incoming request object containing headers.

    Returns:
    - bool: True if the Referer IP is in the valid list, otherwise False.
    """

    valid_hosts = [
    'www.payfast.co.za',
    'sandbox.payfast.co.za',
    'w1w.payfast.co.za',
    'w2w.payfast.co.za',
    ]
    valid_ips = []

    for item in valid_hosts:
        ips = socket.gethostbyname_ex(item)
        if ips:
            for ip in ips:
                if ip:
                    valid_ips.append(ip)
    # Remove duplicates from array
    clean_valid_ips = []
    for item in valid_ips:
        # Iterate through each variable to create one list
        if isinstance(item, list):
            for prop in item:
                if prop not in clean_valid_ips:
                    clean_valid_ips.append(prop)
        else:
            if item not in clean_valid_ips:
                clean_valid_ips.append(item)

    # Security Step 3, check if referrer is valid
    if url_parse(request.headers.get("Referer")).host not in clean_valid_ips:
        return False
    else:
        return True


def pfValidPaymentData(cartTotal, pfData):
    """
    Validates payment data by comparing cart total with the payment data amount.

    Args:
    - cartTotal: Total amount of the cart.
    - pfData: Data received from PayFast.

    Returns:
    - bool: True if the payment data is valid, otherwise False.
    """

    return not (abs(float(cartTotal)) - float(pfData.get('amount_gross'))) > 0.01


def generateSignature(dataArray, pass_phrase=''):
    """
    Generates a signature using provided data and passphrase (if any).

    Args:
    - dataArray: Dictionary containing data for signature generation.
    - pass_phrase: Optional passphrase for additional security.

    Returns:
    - str: The generated MD5 signature string.
    """

    payload = ""
    for key in dataArray:
        # Get all the data from PayFast and prepare parameter string
        payload += key + "=" + urllib.parse.quote_plus(dataArray[key].replace("+", " ")) + "&"
    # After looping through, cut the last & or append your passphrase
    payload = payload[:-1]
    if pass_phrase != '':
        payload += f"&passphrase={pass_phrase}"
    return hashlib.md5(payload.encode()).hexdigest()


def generateApiSignature(dataArray, passPhrase = ''):
    """
    Generates an API signature using provided data and passphrase (if any).

    Args:
    - dataArray: Dictionary containing data for signature generation.
    - passPhrase: Optional passphrase for additional security.

    Returns:
    - str: The generated MD5 API signature string.
    """
    
    payload = ""
    if passPhrase != '':
        dataArray['passphrase'] = passPhrase
    sortedData = sorted(dataArray)
    for key in sortedData:
        # Get all the data from PayFast and prepare parameter string
        payload += key + "=" + urllib.parse.quote_plus(dataArray[key].replace("+", " ")) + "&"
    # After looping through, cut the last & or append your passphrase
    payload = payload[:-1]
    return hashlib.md5(payload.encode()).hexdigest()