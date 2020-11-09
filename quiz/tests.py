from otree.api import Currency as c, currency_range, Submission
from .pages import *
from ._builtin import Bot
from .models import Constants
import random


def mymethd(method, **kwargs):
    p = kwargs.get('player')
    page = kwargs.get('page_class').__name__
    correct_only = page == 'Practice'
    tasks = p.tasks.filter(page=page, answer__isnull=True)
    method(p.id_in_group, {"handshake": True})
    for t in tasks:
        if correct_only:
            answer = str(t.correct_answer)
        else:
            answer = random.choice([str(t.correct_answer), random.randint(0, 100)])
        method(p.id_in_group, {"id": t.id, 'answer': answer})


class PlayerBot(Bot):

    def call_method(self, page_class):
        live_method_name = page_class.live_method
        players = {
            p.id_in_group: p for p in self.group.get_players()
        }

        def method(id_in_group, data):
            return getattr(players[id_in_group], live_method_name)(data)

        mymethd(
            method=method,
            case=self.case,
            round_number=self.round_number,
            page_class=page_class,
            player=self.player
        )

    def play_round(self):
        yield Consent,
        yield Instructions,
        yield Instructions1,
        self.call_method(Practice)
        yield Submission(Practice, check_html=False)
        yield FirstStageAnnouncement,
        self.call_method(Task1)
        yield Submission(Task1, check_html=False)
        yield SecondStageAnnouncement,
        yield Instructions2,
        self.call_method(Task2)
        yield Submission(Task2, check_html=False)
        yield AfterSecondStage,
        yield AcuteStress, {'acute1': random.choice(list(range(0, 11)))}
        yield AcuteStress1, {'acute2': random.choice(list(range(0, 11)))}
        choices = Constants.CHRONIC_CHOICES
        chronics = ChronicStress.form_fields
        answer = {k: random.choice(choices) for k in chronics}
        yield ChronicStress, answer
        correct_answers = Constants.qs.copy()

        for k, v in correct_answers.items():
            j = self.player._meta.get_field(k)
            choices = j.choices
            if choices:
                choice = random.choice(choices)[0]

            r = random.random()
            if r < 0.5:
                if choices:
                    correct_answers[k] = choice
                else:
                    correct_answers[k] = 'aaaaa'
            else:
                correct_answers[k] = correct_answers[k]['correct_answer']
        yield IntellAbility, correct_answers
        yield IntellAbilityResults,
        fields = ['age', 'gender', 'education', 'education1', 'education_other', 'occupation', 'birth', 'game',
                  'money']
        answer = {}
        for f in fields:
            j = self.player._meta.get_field(f)
            choices = j.choices
            if choices:
                choice = random.choice(choices)[0]
            else:
                choice = 'asdf'
            answer[f] = choice
        answer['age'] = random.randint(18, 100)
        yield SocialEconomic, answer
        yield Opinion, {'opinion1':'asdf'}

