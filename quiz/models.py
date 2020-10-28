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

author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'quiz'
    players_per_group = None
    num_rounds = 1
    CHRONIC_CHOICES = ['никогда', 'почти никогда', 'иногда', 'довольно часто', 'часто']
    with open(r'./data/qs.yaml') as file:
        qs = yaml.load(file, Loader=yaml.FullLoader)


class Subsession(BaseSubsession):
    def creating_session(self):
        for p in self.get_players():
            p.get_correct_test_answers()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
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
                correct_answer = qs[i]['correct_answer']
                r.append(dict(label=j.verbose_name,
                              res=res,
                              correct_answer=correct_answer,
                              is_correct=res == correct_answer))
            except AttributeError:
                print("FAIL")
        return r

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
    education1 = models.StringField(label='По какой специальности (направлению подготовки) Вы обучались?',
                                    choices=['экономика или бизнес', 'математика или инженерия', 'естественные науки',
                                             'медицина', 'общественные науки', 'гуманитарные науки', 'искусство',
                                             'другое'],
                                    widget=OtherRadioSelect(other=('другое', 'education_other')))
    education_other = models.StringField(label='')
    birth = models.StringField(label='В какой стране и каком городе Вы родились?')
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
    acute1 = models.StringField(
        label='1)	Вам понравились задания ? Оцените, насколько вам было интересно проходить тест по шкале от 1 до 10, '
              'где 10 – превосходно, очень понравилось , а 1 – ужасно, отвратительно',
        choices=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
        widget=widgets.RadioSelect)
    acute2 = models.StringField(
        label='2)	Оцените по шкале от 1 до 10 насколько вы были напряжены во время прохождения задания, испытывали ли вы стресс и волнение,'
              ' где 1 – был совершенно расслаблен, спокоен, '
              'а 10 – был экстремально напряжен, на грани истерики или нервного срыва.',
        choices=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
        widget=widgets.RadioSelect)
    acute3 = models.StringField(
        label=' 1)	Оцените по шкале от 1 до 10 насколько вы были напряжены, испытывали ли стресс и волнение во время прохождения первого раунда основной части. '
              '( Где горел только таймер, без напоминаний и надписей) '
              '1 – был совершенно расслаблен, спокоен, а 10 – был экстремально напряжен, '
              'на грани истерики или нервного срыва.',
        choices=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
        widget=widgets.RadioSelect)
    acute4 = models.StringField(
        label='2)	Оцените по шкале от 1 до 10 насколько вы были напряжены, испытывали ли стресс и волнение во время прохождения второго раунда основной части. '
              '( Где горел не только таймер, но и высвечивались напоминания и надписи) '
              '1 – был совершенно расслаблен, спокоен, '
              'а 10 – был экстремально напряжен, на грани истерики или нервного срыва',
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
