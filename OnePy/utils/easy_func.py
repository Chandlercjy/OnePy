
from itertools import count

from OnePy.utils.awesome_func import dict_to_table


def check_setting(dict_data, name, check_only=False):
    if dict_data == {}:
        print('>'*10, f'Attention!! There is No {name}!!!', '<'*10)
    else:
        if not check_only:
            counter = count(1)
            print(dict_to_table({f'{name}_{next(counter)}': key
                                 for key in dict_data}))
