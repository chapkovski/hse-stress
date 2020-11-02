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
    return '{} minutes {} seconds'.format(minutes, seconds)
