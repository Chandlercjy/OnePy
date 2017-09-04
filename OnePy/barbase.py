class BarBase(object):
    pass


class Current_bar(BarBase):
    def __init__(self):
        self.cur_bar_list = []

    def add_new_bar(self, new_bar):
        self.cur_bar_list.pop(0) if len(self.cur_bar_list) == 2 else None
        self.cur_bar_list.append(new_bar)

    @property
    def cur_data(self):
        return self.cur_bar_list[0]

    @property
    def next_data(self):
        return self.cur_bar_list[1]

    @property
    def cur_date(self):
        return self.cur_bar_list[0]['date']

    @property
    def cur_open(self):
        return self.cur_bar_list[0]['open']

    @property
    def cur_high(self):
        return self.cur_bar_list[0]['high']

    @property
    def cur_low(self):
        return self.cur_bar_list[0]['low']

    @property
    def cur_close(self):
        return self.cur_bar_list[0]['close']

    @property
    def next_date(self):
        return self.cur_bar_list[1]['date']

    @property
    def next_open(self):
        return self.cur_bar_list[1]['open']

    @property
    def next_high(self):
        return self.cur_bar_list[1]['high']

    @property
    def next_low(self):
        return self.cur_bar_list[1]['low']

    @property
    def next_close(self):
        return self.cur_bar_list[1]['close']
