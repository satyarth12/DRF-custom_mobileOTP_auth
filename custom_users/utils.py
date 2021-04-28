import random
import string
from django.utils.text import slugify
from io import BytesIO

def otp_generator():
    otp = random.randint(999, 9999)
    return otp
