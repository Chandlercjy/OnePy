
from collections import UserDict
from itertools import count

from OnePy.utils.awesome_func import dict_to_table


class UsefulDict(UserDict):

    def __init__(self, name):
        super().__init__(self)
        self.name = name
        self.num = count(1)

    def print_data(self, check_only=False):
        if self.data == {}:
            print('>'*10, f'Attention!! There is No  {self.name}!!!', '<'*10)
        else:
            if not check_only:
                print(dict_to_table({f'{self.name}_{next(self.num)}': key
                                     for key in self.data}))
