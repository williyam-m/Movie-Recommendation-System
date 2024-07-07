from django import template
import time

register = template.Library()

@register.filter
def countkm(value,arg):
    return float(format(int(value) / int(arg), '.2f'))

@register.filter
def timed(value):
    time.sleep(value)
    return None