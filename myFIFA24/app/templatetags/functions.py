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