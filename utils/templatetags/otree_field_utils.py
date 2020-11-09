from django import template
from otree.templatetags.otree_forms import FormFieldNode
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

register = template.Library()
import re


@register.inclusion_tag('utils/tags/joined_form.html', name='joined_form', takes_context=True)
def render_joined_form(context, form):

    joined_fields = getattr(context['view'], 'joined_fields', [])
    return dict(form=form,
                joined_fields=joined_fields,
                fields_order=getattr(context['view'], 'jfields_order', [])
                )
