from django import template
from otree.templatetags.otree_forms import FormFieldNode
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

register = template.Library()
import re
from django import template

register = template.Library()


def pluralize(value, forms):
    """
    Подбирает окончание существительному после числа
    {{someval|pluralize:"товар,товара,товаров"}}
    https://gist.github.com/dpetukhov/cb82a0f4d04f7373293bdf2f491863c8
    """
    try:
        one, two, many = forms.split(u',')
        value = str(value)[-2:]  # 314 -> 14

        if (21 > int(value) > 4):
            return many

        if value.endswith('1'):
            return one
        elif value.endswith(('2', '3', '4')):
            return two
        else:
            return many

    except (ValueError, TypeError):
        return ''


@register.filter
def duration(td):
    minutes, seconds = divmod(td.total_seconds(), 60)
    rus_min = pluralize(int(minutes), 'минута,минуты,минут')
    rus_sec = pluralize(int(seconds), 'секунда,секунды,секунд')
    return f'{int(minutes)} {rus_min} {int(seconds)} {rus_sec}'


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
