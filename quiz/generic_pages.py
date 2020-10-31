from ._builtin import Page as oTreePage

from datetime import datetime, timezone


class Page(oTreePage):
    def get_progress(self):
        totpages = self.participant._max_page_index
        curpage = self.participant._index_in_pages
        return f"{curpage / totpages * 100:.0f}"


class TaskPage(Page):
    def get(self, *args, **kwargs):
        self.participant.vars.setdefault(f'entrance_time_{self.__class__.__name__}', datetime.now(timezone.utc))
        return super().get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        r = super().get_context_data( *args, **kwargs)
        r['name'] = self.__class__.__name__
        return r

    def js_vars(self):
        return self.vars_for_template()

    live_method = 'get_next_task'
