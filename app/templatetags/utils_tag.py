from django import template
from app.utils import *

register = template.Library()

@register.filter()
def index(l, i):
    return l[i]

@register.filter()
def is_even_number(number):
    if number != 0 and number%2 == 0:
        return True
    else:
        return False

@register.filter()
def length_form(form):
    return len(form.fields)
