from ._builtin import Page as oTreePage


class Page(oTreePage):
    def get_progress(self):
        totpages = self.participant._max_page_index
        curpage = self.participant._index_in_pages
        return f"{curpage / totpages * 100:.0f}"


class TaskPage(Page):
    def vars_for_template(self):
        return dict(name=self.__class__.__name__)

    def js_vars(self):
        return self.vars_for_template()

    live_method = 'get_next_task'
