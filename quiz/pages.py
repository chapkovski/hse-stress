from otree.api import Currency as c, currency_range
from ._builtin import WaitPage
from .generic_pages import Page, TaskPage
from .models import Constants
from django.db.models import Sum
from datetime import datetime, timezone, timedelta


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


class Task1(TaskPage):
    max_time_for_tasks = 30
    sec_before_end_warning = 2

    def get_max_time_for_tasks(self):
        return self.max_time_for_tasks

    def is_displayed(self):
        return not self.player.game_over_task1

    def vars_for_template(self):
        entrance_time = self.participant.vars['entrance_time_Task1']
        endtime = entrance_time + timedelta(seconds=self.get_max_time_for_tasks())
        time_till_end = (endtime - datetime.now(timezone.utc)).total_seconds()
        return dict(time_till_end=time_till_end,
                    show_warning=time_till_end <= self.sec_before_end_warning,
                    sec_before_end_warning=self.sec_before_end_warning
                    )

    def before_next_page(self):
        entrance_time = self.participant.vars[f'entrance_time_Task1']
        print(datetime.now(timezone.utc) - entrance_time, "POST TIME")


class SecondStageAnnouncement(Page):
    pass


class Task2(TaskPage):
    """we should generate/check out here the number of tasks based on how many were done at task1 stage"""
    template_name = 'quiz/Task1.html'
    max_time_for_tasks = Task1.max_time_for_tasks
    sec_before_end_warning = Task1.sec_before_end_warning

    def get_sec_before_end_warning(self):
        if self.session.config.get('tp'):
            return self.get_max_time_for_tasks()
        else:
            return self.sec_before_end_warning

    def get_max_time_for_tasks(self):
        """
        we get all the time he/she spends on no-pressure tasks in period 1

        :return: number of seconds spent on tasks
        :rtype: integer
        """
        if not self.session.config.get('tp'):
            return self.max_time_for_tasks

        underthreat = self.player.tasks.filter(under_threat=False,
                                               answer__isnull=False, ). \
            aggregate(totsec=Sum('seconds_on_task'))['totsec']
        print("BASE TIME", underthreat.total_seconds())
        return (underthreat.total_seconds()) * 1  # Constants.time_pressure_coef

    def is_displayed(self):
        return not self.player.game_over_task2

    def vars_for_template(self):
        sec_before = self.get_sec_before_end_warning()
        entrance_time = self.participant.vars['entrance_time_Task2']
        endtime = entrance_time + timedelta(seconds=self.get_max_time_for_tasks())
        time_till_end = (endtime - datetime.now(timezone.utc)).total_seconds()
        return dict(time_till_end=time_till_end,
                    show_warning=time_till_end <= sec_before,
                    sec_before_end_warning=sec_before
                    )


class Results(Page):
    def get_timeout_seconds(self):
        return self.player.age


page_sequence = [
    # SocialEconomic,
    # IntellAbility,
    # IntellAbilityResults,
    # AcuteStress,
    # IQ,
    Task1,
    SecondStageAnnouncement,
    Task2,
    # AcuteStress1,
    # ChronicStress,
    # ChronicStressResults,
    # Results,
]

assert set(Constants.num_tasks.keys()).issubset(set([i.__name__ for i in page_sequence]))
