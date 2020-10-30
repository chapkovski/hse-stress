from otree.api import Currency as c, currency_range
from ._builtin import WaitPage
from .generic_pages import Page
from .models import Constants


class SocialEconomic(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'education', 'education1', 'education_other', 'birth', 'game', 'money', ]


class IntellAbility(Page):
    form_model = 'player'
    form_fields = ['test1', 'test2', 'test3', 'test4', 'test6', 'test8', 'test9', 'test10']

    def before_next_page(self):
        r = self.player.get_correct_test_answers()
        self.player.correct_tests = sum([1 for i in r if i.get('is_correct')])
        self.player.total_tests = len(r)



class IntellAbilityResults(Page):
    pass


class AcuteStress(Page):
    form_model = 'player'
    form_fields = ['acute1', 'acute2']


class AcuteStress1(Page):
    form_model = 'player'
    form_fields = ['acute3', 'acute4']


class ChronicStress(Page):
    form_model = 'player'
    form_fields = ['chronic1', 'chronic2', 'chronic3', 'chronic4', 'chronic5', 'chronic6', 'chronic7',
                   'chronic8', 'chronic9', 'chronic10']


class IQ(Page):
    pass


class Matrices(Page):
    pass


class Results(Page):
    def get_timeout_seconds(self):
        return self.player.age


page_sequence = [
    # SocialEconomic,
    IntellAbility,
    IntellAbilityResults,
    # AcuteStress,
    # IQ,
    # Matrices,
    # AcuteStress1,
    # ChronicStress,
    # ChronicStressResults,
    # Results,
]
