

from OnePy.utils.awesome_func import dict_to_table
from collections import UserDict

class UsefulDict(UserDict):

    def __init__(self, name):
        super().__init__(self)
        self.name = name

    def print_data(self, show_name=False):
        if self.data == {}:
            print('>'*10, f'Attention!! There is No  {self.name}!!!', '<'*10)
        else:
            print(">"*5, self.name) if show_name else None
            print(dict_to_table({key: str(value.__class__.__name__)
                                 for key, value in self.data.items()}))
