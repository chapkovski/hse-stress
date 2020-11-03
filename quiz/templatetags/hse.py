from django import template
from otree.templatetags.otree_forms import FormFieldNode
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

register = template.Library()
import re
from django import template

register = template.Library()


@register.filter
def duration(td):
    total_seconds = int(td.total_seconds())
    minutes = total_seconds // 60
    seconds = td.seconds
    return '{} минут {} секунд'.format(minutes, seconds)

@register.filter
def q_ending(value):
    value = str(value)
    p = re.compile(r'^(?P<value>\d+)')
    m = p.search(value)
    re_val = m.group('value')
    if re_val:
        lasttwo = int(re_val[-2:]) if len(re_val) > 2 else int(re_val)
        lastdigit = int(re_val[-1])
        if 5 <= lasttwo <= 20:
            r = 'вопросов'
        elif 2 <= lastdigit <= 4:
            r = 'вопроса'
        elif lastdigit == 1:
            r = 'вопрос'
        else:
            r = 'вопросов'
        return re_val + " " + r
    return value
