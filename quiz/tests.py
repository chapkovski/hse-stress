from otree.api import Currency as c, currency_range, Submission
from . import pages
from ._builtin import Bot
from .models import Constants
import random


def mymethd(method, **kwargs):
    p = kwargs.get('player')
    page = kwargs.get('page_class').__name__
    tasks = p.tasks.filter(page=page, answer__isnull=True)
    method(p.id_in_group, {"handshake": True})
    for t in tasks:
        answer = random.choice([str(t.correct_answer), random.randint(0, 100)])
        method(p.id_in_group, {"id": t.id, 'answer':answer})

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
        self.call_method(pages.Task1)
        yield Submission(pages.Task1, check_html=False)
        self.call_method(pages.Task2)
        yield Submission(pages.Task2, check_html=False)
