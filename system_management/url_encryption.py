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

from cryptography.fernet import Fernet
import base64
import logging
import traceback
from django.conf import settings

#this is your "password/ENCRYPT_KEY". keep it in settings.py file
#key = Fernet.generate_key()

def encrypt(txt):
    """
    Encrypts a string using Fernet symmetric encryption.

    Args:
    - txt (str): The text to be encrypted.

    Returns:
    - str or None: Encrypted text in URL-safe base64 format or None if an error occurs.
    """
    try:
        # Convert integer etc to string first
        txt = str(txt)
        # Get the key from settings
        cipher_suite = Fernet(settings.ENCRYPT_KEY) # key should be byte
        # Input should be byte, so convert the text to byte
        encrypted_text = cipher_suite.encrypt(txt.encode('ascii'))
        # Encode to urlsafe base64 format
        encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode("ascii")
        return encrypted_text
    except Exception as e:
        # Log the error if any
        print(e)
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None


def decrypt(txt):
    """
    Decrypts a string previously encrypted using Fernet symmetric encryption.

    Args:
    - txt (str): The encrypted text in URL-safe base64 format.

    Returns:
    - str or None: Decrypted text or None if an error occurs.
    """
    try:
        # Base64 decode
        txt = base64.urlsafe_b64decode(txt)
        cipher_suite = Fernet(settings.ENCRYPT_KEY)
        decoded_text = cipher_suite.decrypt(txt).decode("ascii")
        return decoded_text
    except Exception as e:
        # Log the error
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None