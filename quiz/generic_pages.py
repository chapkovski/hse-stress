from ._builtin import Page as oTreePage

from datetime import datetime, timezone
from django.db.models import Sum

import logging
logger = logging.getLogger(__name__)
class Page(oTreePage):
    def get_progress(self):
        totpages = self.participant._max_page_index
        curpage = self.participant._index_in_pages
        return f"{curpage / totpages * 100:.0f}"


class TaskPage(Page):
    practice = False

    def get(self, *args, **kwargs):
        self.participant.vars.setdefault(f'entrance_time_{self.__class__.__name__}', datetime.now(timezone.utc))
        return super().get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        r = super().get_context_data(*args, **kwargs)
        r['name'] = self.__class__.__name__
        return r

    def js_vars(self):
        r = self.vars_for_template()
        r['name'] = self.__class__.__name__
        return r

    live_method = 'get_next_task'

    def before_next_page(self):
        page = self.__class__.__name__
        stage = page[-1]
        if not self.practice:
            time_spent_on_tasks = self.player.tasks.filter(under_threat=False,
                                                           answer__isnull=False, page=page). \
                aggregate(totsec=Sum('seconds_on_task'))['totsec']

            performance = self.player.tasks.filter(is_correct=True, page=page).count()
            total_submitted = self.player.tasks.filter(answer__isnull=False, page=page).count()
            if performance > 0:
                productivity = performance / (
                        time_spent_on_tasks.total_seconds() / 60)
            else:
                productivity = 0
            items_to_assign = ((f'time_spent_on_tasks_{stage}', time_spent_on_tasks),
                               (f'total_submitted_{stage}', total_submitted),
                               (f'performance_{stage}', performance),
                               (f'productivity_{stage}', productivity))
            for k, v in items_to_assign:
                setattr(self.player, k, v)
            logger.info("ITEMS TO ASSIGN", items_to_assign)


class AnnouncementPage(Page):
    pointer_page = None

    def vars_for_template(self):
        total_tasks_pointer = self.player.get_total_tasks(self.pointer_page)
        correct_tasks_pointer = self.player.get_correct_tasks(self.pointer_page)
        get_time_for_tasks_pointer = self.player.get_time_spent_tasks(self.pointer_page)
        return dict(correct_tasks=correct_tasks_pointer,
                    total_tasks=total_tasks_pointer,
                    get_time_for_tasks=get_time_for_tasks_pointer,
                    tp=self.session.config.get('tp')
                    )
