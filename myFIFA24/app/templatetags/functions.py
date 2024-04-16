from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='compute_wr')
@stringfilter
def compute_wr(attr):
    if attr == '2':
        return 'H'
    elif attr == '1':
        return 'L'
    elif attr == '0':
        return 'M'

@register.filter(name='compute_foot')
@stringfilter
def compute_foot(attr):
    if attr == '1':
        return 'Left'
    elif attr == '2':
        return 'Right'