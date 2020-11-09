from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)
from .widgets import OtherRadioSelect
import yaml
from django.db import models as djmodels
import logging
import random
from string import digits
from django.template.loader import render_to_string
from datetime import datetime, timezone, timedelta
from django.db.models import Sum

logger = logging.getLogger(__name__)
author = 'Philip Chapkovski, HSE-Moscow'

doc = """
Stress-related study by Hennig-Schmidt, Chapkovski, Kartavtseva
"""


class Constants(BaseConstants):
    secs_for_first_tasks = 20
    name_in_url = 'quiz'
    players_per_group = None
    num_rounds = 1
    CHRONIC_CHOICES = ['никогда', 'почти никогда', 'иногда', 'довольно часто', 'часто']
    check_for_correction = ['Practice']  # list of pages where we check for correct answers
    time_pressure_coef = 0.65
    num_tasks = dict(
        Practice=2,
        Task1=10,
        Task2=10,
    )
    task_len = 100
    num_rows = 10
    max_time_for_tasks = 600

    assert task_len % num_rows == 0
    with open(r'./data/qs.yaml') as file:
        qs = yaml.load(file, Loader=yaml.FullLoader)


def chunks(l, n):
    """Yield n number of striped chunks from l."""
    for i in range(0, n):
        yield l[i::n]


class Subsession(BaseSubsession):
    treatment = models.StringField()

    def creating_session(self):
        if self.session.config.get('tp') and self.session.config.get('stress'):
            self.treatment = 'stress+tp'
        elif self.session.config.get('tp'):
            self.treatment = 'tp only'
        else:
            self.treatment = 'baseline'
        sqs = []
        for p in self.get_players():
            for page, num_tasks in Constants.num_tasks.items():
                for t in range(num_tasks):
                    item_to_check = random.choice(digits)
                    body = random.choices(digits, k=Constants.task_len)

                    correct_answer = sum([1 for i in body if i == item_to_check])
                    sqs.append(Task(owner=p, body=''.join(body),
                                    page=page,
                                    item_to_check=item_to_check,
                                    correct_answer=correct_answer
                                    ))

        Task.objects.bulk_create(sqs)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    part_for_payment = models.IntegerField(choices=[0, 1])
    correct_tests = models.IntegerField()
    total_tests = models.IntegerField()
    show_threat_task1 = models.BooleanField(initial=False)
    show_threat_task2 = models.BooleanField(initial=False)
    game_over_task1 = models.BooleanField(initial=False)
    game_over_task2 = models.BooleanField(initial=False)

    performance_1 = models.IntegerField()
    performance_2 = models.IntegerField()
    total_submitted_1 = models.IntegerField()
    total_submitted_2 = models.IntegerField()
    time_spent_on_tasks_1 = djmodels.DurationField(null=True)
    time_spent_on_tasks_2 = djmodels.DurationField(null=True)
    productivity_1 = models.FloatField()
    productivity_2 = models.FloatField()

    def _get_answered_tasks(self, page):
        return self.tasks.filter(page=page, answer__isnull=False)

    def get_time_spent_tasks(self, page):
        """
        returns total time spent on solving task at the specific page (Practice, Task1, Task2)
        """
        ts = self._get_answered_tasks(page)
        return ts.aggregate(totsec=Sum('seconds_on_task'))['totsec']

    def get_total_tasks(self, page):
        """
        returns total number of tasks solved at the specific page (Practice, Task1, Task2)
        """
        ts = self._get_answered_tasks(page)
        return ts.count()

    def get_correct_tasks(self, page):
        """
        returns number of  *CORRECT* tasks solved at the specific page (Practice, Task1, Task2)
        """
        ts = self._get_answered_tasks(page)
        return ts.filter(is_correct=True).count()

    def time_for_task_2(self):
        if self.session.config.get('tp'):
            return self.time_spent_on_tasks_1 * Constants.time_pressure_coef
        return timedelta(seconds=Constants.max_time_for_tasks)

    def _tasks_info(self):
        page = self.participant._current_page_name
        r = dict(cur=None, total=None)
        tasks = self.tasks.filter(page=page)
        if tasks.exists():
            r['cur'] = tasks.filter(answer__isnull=False).count() + 1
            r['total'] = tasks.count()
        return r

    def cur_task_num(self):
        return self._tasks_info()['cur']

    def total_tasks(self):
        return self._tasks_info()['total']

    def render_q(self, q):
        """
        We get the question item and render it for html
        """
        resp = dict(body=render_to_string('./quiz/components/matrix.html',
                                          {'data': chunks(list(q.body), Constants.num_rows)}),
                    item_to_check=q.item_to_check,
                    id=q.id,
                    cur_task_num=self.cur_task_num(),
                    )
        if self.session.is_demo:
            resp['correct_answer'] = q.correct_answer
        return resp

    def get_next_task(self, data):
        """
        We get the user response from live page and return something here (mostly the next task)
        """
        logger.info(data)
        page = data.get('page', self.participant._current_page_name)
        if data.get('game_over'):
            setattr(self, f'game_over_{page.lower()}', True)
            return
        if data.get('show_threat'):
            setattr(self, f'show_threat_{page.lower()}', True)
            return {self.id_in_group: dict(show_reminder=True)}

        qid = data.get('id')
        answer = data.get('answer')

        check_for_correction = page in Constants.check_for_correction

        if answer and qid:
            q = Task.objects.get(id=qid)
            q.post_time = datetime.now(timezone.utc)

            q.seconds_on_task = (q.post_time - q.get_time)
            q.num_seconds_on_task = q.seconds_on_task.total_seconds()
            q.answer = int(answer)
            q.is_correct = q.correct_answer == q.answer
            if not q.is_correct and check_for_correction:
                """We return back the q with the warning that it's not correct"""
                resp = self.render_q(q)
                resp['wrong_answer'] = True
                return {self.id_in_group: resp}
            try:
                q.under_threat = getattr(self, f'show_threat_{page.lower()}')
            except AttributeError:
                pass  # that should be a practice page
            q.save()
        next_q = self._next_task(page)
        if next_q:
            logger.info(f'Correct answer for the task: {next_q.correct_answer}')
            if not next_q.get_time:
                next_q.get_time = datetime.now(timezone.utc)
                next_q.save()
            resp = self.render_q(next_q)
            r = {self.id_in_group: resp}
            return r
        return {self.id_in_group: dict(no_tasks_left=True)}

    def _next_task(self, page):
        """
        Internal method to retrieve next tsk
        """
        unanswered = self.tasks.filter(answer__isnull=True, page=page)
        if unanswered.exists():
            q = unanswered.first()
            return q

    def get_correct_test_answers(self):
        qs = Constants.qs
        testqs = list(qs.keys())
        r = []
        for i in testqs:
            try:
                j = self._meta.get_field(i)
                res = getattr(self, i)
                if isinstance(res, str):
                    res = res.lower()
                else:
                    res = ''
                correct_answer = str(qs[i]['correct_answer'])
                r.append(dict(label=j.verbose_name,
                              res=res,
                              correct_answer=correct_answer,
                              is_correct=res == correct_answer))
            except AttributeError:
                print("FAIL")
        return r

    def set_payoff(self):
        self.payoff = (self.performance_1 + self.performance_2) * self.session.config.get('fee_per_task', 0.1)

    def full_payoff(self):
        return self.session.config.get('toloka_participation_fee', 0) + self.payoff.to_real_world_currency(self.session)

    age = models.IntegerField(min=18, max=101, label=' Сколько Вам лет?')
    gender = models.StringField(label='Укажите Ваш пол?',
                                widget=widgets.RadioSelect,
                                choices=['Мужской', 'Женский'],
                                )
    education = models.StringField(label='Какой у вас уровень образования?',
                                   choices=['Неполное среднее (8-9 классов)', 'Среднее общее (10-11 классов)',
                                            'Среднее профессиональное (училище)',
                                            'Среднее специальное - техническое (техникум)',
                                            'Неполное высшее образование (не менее 3-х лет обучения)',
                                            'Высшее образование', 'Аспирантура'],
                                   widget=widgets.RadioSelect
                                   )
    education1 = models.StringField(
        label='В случае если у Вас имеется высшее образование, отметьте, пожалуйста, по какой специальности (направлению подготовки) Вы обучались?',
        choices=['экономика или бизнес', 'математика или инженерия', 'естественные науки',
                 'медицина', 'общественные науки', 'гуманитарные науки', 'искусство',
                 'другое'],
        widget=OtherRadioSelect(other=('другое', 'education_other')))
    education_other = models.StringField(label='', blank=True)
    birth = models.StringField(label='В какой стране и каком городе Вы родились?')
    occupation = models.StringField(
        label='Пожалуйста, укажите, по какой профессии/специальности вы работаете. Если Вы не работаете или самозаняты, то тоже укажите это')

    game = models.StringField(
        label='Если я вовлечен в какую-либо игру, мне всегда хочется победить. Насколько Вы согласны с данным утверждением? '
              '(Oтвет: шкала от 1 до 5, где 1 – полностью не согласен, а 5 – полностью согласен)',
        choices=['1', '2', '3', '4', '5'],
        widget=widgets.RadioSelect)
    money = models.StringField(
        label='Какое из описаний точнее всего соответствует материальному положению Вашей семьи?',
        choices=['денег не хватает даже на питание',
                 'на питание денег хватает, но не хватает на покупку одежды и обуви',
                 'на покупку одежды и обуви денег хватает, но не хватает на покупку крупной бытовой техники',
                 'денег хватает на покупку крупной бытовой техники, но мы не можем купить новую машину',
                 'на новую машину денег хватает, но мы не можем позволить себе покупку  квартиры или дома',
                 'материальных затруднений не испытываем, при необходимости могли бы приобрести квартиру, дом',
                 'затрудняюсь ответить'],
        widget=widgets.RadioSelect)
    test1 = models.StringField(label='Что значит слово "умиротворять"?',
                               choices=['выстраивать', 'успокаивать', 'обтёсывать', 'устанавливать'],
                               widget=widgets.RadioSelect)

    test2 = models.StringField(label='Какое число лишнее?',
                               choices=['4519', '2718', '4915', '9514', '6328', '5617'],
                               widget=widgets.RadioSelect)
    test3 = models.StringField(
        label='Впишите в скобки слово, которое обозначает то же, что определения, расположенные по обеим сторонам скобок:'
              'плавильная печь (?) музыкальный инструмент')
    test4 = models.StringField(
        label='Из левого числа получается правое число по одной и той же формуле. Что за число вместо знака вопроса? '
              '12...2'
              '3... - 1'
              ' 18... 4'
              '9... ?')
    test6 = models.StringField(
        label='Образуйте слово состоящее из 6 букв, использовав следующие буквы: ТАПНЕ. (Уточнение: '
              'одну букву можно использоваться несколько раз')
    test8 = models.StringField(
        label='Каким числом следует заменить знак вопроса? 1, 2, 4, 6, 9, 12, 15, 19, 23, 27, 31, ?')
    test9 = models.StringField(label='Упростите выражение: 24/18:56/9:3/34',
                               choices=['4/3', '3/7', '3/4', '7/8', '17/9', '17/7'],
                               widget=widgets.RadioSelect)
    test10 = models.StringField(
        label='Угадайте слово, которое стоит в алфавитном порядке между данными словами и удовлетворяет подсказке: '
              'знак - (обладание какими-либо сведениями) - знахарь')
    acute1 = models.IntegerField(
        label='Оцените по шкале от 1 до 10, насколько вы были напряжены во время прохождения последних 10 заданий, испытывали ли вы стресс и волнение,'
              ' где 1 – был совершенно расслаблен, спокоен, '
              'а 10 – был максимально напряжен:',
        choices=list(range(0,11)),
        widget=widgets.RadioSelect)
    acute2 = models.IntegerField(
        label='Оцените по шкале от 1 до 10, насколько вы были напряжены во время прохождения первой части теста (первые 10 заданий), испытывали ли вы стресс и волнение,'
              ' где 1 – был совершенно расслаблен, спокоен, '
              'а 10 – был максимально напряжен:',
        choices=list(range(0,11)),
        widget=widgets.RadioSelect)
    acute3 = models.StringField(
        label=' Оцените по шкале от 1 до 10, насколько вы были напряжены, испытывали ли стресс и волнение во время прохождения первого раунда основной части. '
              '1 – был совершенно расслаблен, спокоен, а 10 – был экстремально напряжен, '
              'на грани истерики или нервного срыва:',
        choices=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
        widget=widgets.RadioSelect)
    acute4 = models.StringField(
        label='Оцените по шкале от 1 до 10, насколько вы были напряжены, испытывали ли стресс и волнение во время прохождения второго раунда основной части. '
              '1 – был совершенно расслаблен, спокоен, '
              'а 10 – был экстремально напряжен, на грани истерики или нервного срыва:',
        choices=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
        widget=widgets.RadioSelect)
    chronic1 = models.StringField(
        label='Как часто за последний месяц вы испытывали беспокойство из-за непредвиденных событий?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic2 = models.StringField(
        label='Как часто за последний месяц Вам казалось сложным контролировать важные события Вашей жизни?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic3 = models.StringField(label='Как часто за последний месяц Вы испытывали нервное напряжение или стресс?',
                                  choices=Constants.CHRONIC_CHOICES,
                                  widget=widgets.RadioSelect)
    chronic4 = models.StringField(
        label=' Как часто за последний месяц Вы чувствовали уверенность в том, что справитесь с решением ваших личных проблем?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic5 = models.StringField(
        label='Как часто за последний месяц Вы чувствовали, что все идет так, как Вы этого хотели?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic6 = models.StringField(
        label='Как часто за последний месяц Вы думали, что не можете справиться с тем, что вам нужно сделать?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic7 = models.StringField(
        label='Как часто за последний месяц Вы были в состоянии справиться с вашей раздражительностью?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic8 = models.StringField(label='Как часто за последний месяц Вы чувствовали, что владеете ситуацией?',
                                  choices=Constants.CHRONIC_CHOICES,
                                  widget=widgets.RadioSelect)
    chronic9 = models.StringField(
        label='Как часто за последний месяц Вы чувствовали раздражение из-за того, что происходящие события выходили из-под вашего контроля?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic10 = models.StringField(
        label='Как часто за последний месяц вам казалось, что накопившиеся трудности достигли такого предела, что Вы не могли их контролировать?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)

    opinion1 = models.LongStringField(
        label='Расскажите, пожалуйста, понравилось ли Вам исследование и какие у Вас есть замечания')


class Task(djmodels.Model):
    owner = djmodels.ForeignKey(to=Player, on_delete=djmodels.CASCADE, related_name="tasks")
    body = models.StringField()
    correct_answer = models.IntegerField()
    item_to_check = models.IntegerField()
    answer = models.IntegerField()
    page = models.StringField()
    under_threat = models.BooleanField()
    post_time = djmodels.DateTimeField(null=True)
    get_time = djmodels.DateTimeField(null=True)
    seconds_on_task = djmodels.DurationField(null=True)
    num_seconds_on_task = models.FloatField()
    is_correct = models.BooleanField()

    def __str__(self):
        return f'Task: "{self.body}" for participant {self.owner.participant.code}; correct answer {self.correct_answer}'


def custom_export(players):
    yield ['session', 'code', 'body', 'answer', 'correct_answer', 'is_correct', 'item_to_check', 'page', 'under_threat',
           'get_time', 'post_time', 'sec_on_task', 'num_seconds_on_task']
    for q in Task.objects.order_by('id'):
        yield [q.owner.session.code, q.owner.participant.code, q.body, q.answer, q.correct_answer,
               q.is_correct,
               q.item_to_check,
               q.page, q.under_threat, q.get_time, q.post_time, q.seconds_on_task, q.num_seconds_on_task]
