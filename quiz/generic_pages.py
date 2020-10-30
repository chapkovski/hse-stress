from ._builtin import Page as oTreePage


class Page(oTreePage):
    def get_progress(self):
        totpages = self.participant._max_page_index
        curpage = self.participant._index_in_pages
        return f"{curpage / totpages * 100:.0f}"
