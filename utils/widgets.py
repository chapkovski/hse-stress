from otree.forms.widgets import RadioSelect
from django import forms
import random
import string


def get_random_string(length):
    # https://pynative.com/python-generate-random-string/
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


class OtherRadioSelect(RadioSelect):
    template_name = 'utils/widgets/other.html'

    def __init__(self, other=None, *args, **kwargs):
        self.other = other
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        c = super().get_context(name, value, attrs)
        c['other'] = self.other
        return c


class LikertWidget(forms.RadioSelect):
    template_name = 'utils/widgets/likert.html'

    class Media:
        css = {
            'all': (
                'utils/css/likert.css',
            )
        }
        js = (
            'https://unpkg.com/vue@2.6.12/dist/vue.js',

        )

    def __init__(self, range, *args, **kwargs):
        self.range = range
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        context.update(dict(range=list(self.range),
                            random_id=get_random_string(10)
                            )
                       )
        return context
